import asyncio
import json
import uuid
from datetime import date, timedelta
from multiprocessing import Manager, Process

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.crud import get_prices_light
from app.database import get_db
from app.schemas import PairSelectionRequest
from app.services.backtesting.tasks.pairs_manager import run_pair_selection_task, monitor_pair_selection_progress
from app.stores.task_stores import pairs_tasks_store as tasks_store


router = APIRouter()

# === Start task endpoint ===
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


# === Stream progress SSE ===
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


# === Retrieve final results ===
@router.get("/select/results/{task_id}")
def get_pair_selection_results(task_id: str):
    task = tasks_store.get(task_id)
    if not task:
        return JSONResponse({"detail": "Task not found"}, status_code=404)

    if task.get("status") != "done" or "results" not in task:
        return JSONResponse({"detail": "Task still running or no results yet"}, status_code=202)

    return task["results"]
