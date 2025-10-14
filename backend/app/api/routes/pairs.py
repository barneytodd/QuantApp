from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from multiprocessing import Manager, Process
import asyncio, json, uuid, os

from app.database import get_db
from app.schemas import PairSelectionRequest
from app.services.backtesting.engines.pairs_selection import analyze_pairs
from app.utils.pair_selection import select_pairs_max_weight
from app.crud import get_prices_light
from app.tasks import pairs_tasks_store as tasks_store 
from datetime import date, timedelta

router = APIRouter()


# === 1. Background worker ===
def run_pair_selection_task(task_id, symbols, prices_dict, w_corr, w_coint, progress_state):
    def progress_callback(done, total):
        progress_state["done"] = done
        progress_state["total"] = total
        progress_state["status"] = "running"

    try:
        pairs = analyze_pairs(
            symbols,
            prices_dict,
            w_corr=w_corr,
            w_coint=w_coint,
            progress_callback=progress_callback,
        )
        selected = select_pairs_max_weight(pairs, weight_key="score")

        progress_state.update({
            "done": len(pairs),
            "total": len(pairs),
            "status": "done",
            "results": {"all_pairs": pairs, "selected_pairs": selected},
        })
    except Exception as e:
        progress_state.update({"status": "failed", "error": str(e)})



# === 2. Async listener for progress ===
async def monitor_pair_selection_progress(task_id: str, progress_state):
    """Poll the shared progress dict periodically and mirror to tasks_store."""
    tasks_store[task_id] = dict(progress_state)

    while True:
        # Copy current state into local store
        tasks_store[task_id] = dict(progress_state)

        if progress_state.get("status") in ("done", "failed"):
            break

        await asyncio.sleep(0.2)


# === 3. Start task endpoint ===
@router.post("/select/start")
async def start_pair_selection(req: PairSelectionRequest, db: Session = Depends(get_db)):
    # Fetch price data
    end = date.today()
    start = end - timedelta(days=365)
    lookback = 0
    rows = get_prices_light(db, req.symbols, start, end, lookback)

    # Build prices_dict grouped by symbol
    prices_dict = {}
    for r in rows:
        prices_dict.setdefault(r["symbol"], []).append({
            "date": r["date"],
            "close": r["close"],
        })

    if len(prices_dict) < 2:
        raise HTTPException(status_code=404, detail="Not enough price data for selected symbols")

    task_id = str(uuid.uuid4())
    manager = Manager()
    progress_state = manager.dict(done=0, total=0, status="starting", results=None)

    # Create subprocess
    p = Process(
        target=run_pair_selection_task,
        args=(task_id, req.symbols, prices_dict, req.w_corr, req.w_coint, progress_state)
    )
    p.start()

    # Start async listener for progress
    asyncio.create_task(monitor_pair_selection_progress(task_id, progress_state))

    tasks_store[task_id] = {"status": "starting", "done": 0, "total": 0}
    return {"task_id": task_id, "status": "started"}


# === 4. Stream progress SSE ===
@router.get("/select/stream/{task_id}")
async def stream_pair_selection_progress(task_id: str):
    async def event_generator():
        last_state = {}

        while True:
            task = tasks_store.get(task_id)
            if not task:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            snapshot = {
                "done": task.get("done", 0),
                "total": task.get("total", 0),
                "status": task.get("status", "unknown"),
            }

            if snapshot != last_state:
                last_state = snapshot.copy()
                yield f"data: {json.dumps(snapshot)}\n\n"

            if task["status"] in ("done", "failed"):
                yield f"data: {json.dumps({'done': True, 'status': task['status']})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# === 5. Retrieve final results ===
@router.get("/select/results/{task_id}")
def get_pair_selection_results(task_id: str):
    task = tasks_store.get(task_id)
    if not task:
        return JSONResponse({"detail": "Task not found"}, status_code=404)

    if task.get("status") != "done" or "results" not in task:
        return JSONResponse({"detail": "Task still running or no results yet"}, status_code=202)

    return task["results"]
