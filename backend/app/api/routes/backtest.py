from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Process
import json, asyncio, os, uuid

from app.database import get_db
from app.schemas import StrategyRequest
from app.services.backtesting.helpers.data.data_preparation import prepare_backtest_inputs, create_walkforward_windows
from app.services.backtesting.helpers.data.data_aggregation import compute_walkforward_results, aggregate_walkforward_results


from app.services.backtesting.tasks.tasks import run_segment
from app.services.backtesting.engines.backtest_engine import run_backtest
from app.utils.data_helpers import fetch_price_data, fetch_price_data_light
from app.tasks import walkforward_tasks_store as tasks_store


router = APIRouter()


# === 1. Standard full-period backtest ===
@router.post("/backtest")
def run_standard_backtest(payload: StrategyRequest, db: Session = Depends(get_db)):
    try:
        all_symbols, strategy_symbols, params, lookback = prepare_backtest_inputs(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = fetch_price_data(db, all_symbols, params["startDate"], params["endDate"], lookback)

    print("Running standard backtest...")
    results = run_backtest(data, strategy_symbols, params, lookback)
    print("Completed.")

    if not results:
        raise HTTPException(status_code=404, detail="No price data found for given symbols")

    return results


# === 2. Walkforward async engine ===
async def run_walkforward_async(task_id, windows, all_symbols, strategy_symbols, params, lookback, db, window_length=3):
    manager = Manager()
    progress_state = manager.dict()
    progress_state["segments"] = manager.dict()
    progress_state["results"] = manager.dict()
    progress_state["overall_progress"] = 0.0
    progress_state["done_segments"] = 0

    # Initialize task in store
    tasks_store[task_id] = {
        "status": "running",
        "progress": {},
        "overall_progress": 0.0,
        "results": {},
        "total_segments": len(windows),
        "window_length": window_length
    }

    for seg_id, window in enumerate(windows, start=1):
        progress_state["segments"][seg_id] = manager.dict(progress_pct=0.0, done=False)

    # Kick off listener that mirrors progress_state into tasks_store
    asyncio.create_task(sync_progress_state_to_store(task_id, progress_state))

    with ProcessPoolExecutor(max_workers=os.cpu_count() - 1 or 3) as pool:
        loop = asyncio.get_running_loop()
        tasks = []

        for seg_id, window in enumerate(windows, start=1):
            data = fetch_price_data_light(db, all_symbols, window["start"], window["end"], lookback)
            # submit run_segment using pool executor
            tasks.append(loop.run_in_executor(
                pool,
                run_segment,
                seg_id, data, strategy_symbols, params, lookback, progress_state
            ))

        await asyncio.gather(*tasks)

    progress_state["done_segments"] = len(windows)
    progress_state["overall_progress"] = 100.0
    tasks_store[task_id]["status"] = "done"

async def sync_progress_state_to_store(task_id, progress_state):
    """Continuously mirror the Manager dictionary into tasks_store."""

    while tasks_store[task_id]["status"] == "running":
        total_segments = len(progress_state["segments"])
        if total_segments == 0:
            await asyncio.sleep(0.2)
            continue

        # Compute aggregate progress
        overall = sum(seg["progress_pct"] for seg in progress_state["segments"].values()) / total_segments
        tasks_store[task_id]["overall_progress"] = overall

        # Mirror segment data
        for seg_id, seg_data in progress_state["segments"].items():
            tasks_store[task_id]["progress"][seg_id] = {
                "progress_pct": seg_data["progress_pct"],
                "done": seg_data["done"],
            }

        # Mirror results as they arrive
        for seg_id, result in progress_state["results"].items():
            tasks_store[task_id]["results"][seg_id] = result

        await asyncio.sleep(0.3)


# === 3. Launch walkforward task ===
@router.post("/backtest/walkforward/start")
async def start_walkforward_backtest(
    payload: StrategyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    print("Received walkforward start payload")
    try:
        all_symbols, strategy_symbols, params, lookback = prepare_backtest_inputs(payload)
    except ValueError as e:
        print("Error preparing backtest inputs:", e)
        raise HTTPException(status_code=400, detail=str(e))

    windows = create_walkforward_windows(params["startDate"], params["endDate"], window_length=1)
    if not windows:
        print("Error creating walk-forward windows")
        raise HTTPException(status_code=400, detail="Invalid walk-forward configuration")

    window_length = 3
    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {
        "progress": {},
        "results": {},
        "status": "pending",
        "overall_progress": 0.0,
        "total_segments": len(windows),
        "window_length": window_length
    }

    # Launch async walkforward execution in background
    asyncio.create_task(run_walkforward_async(task_id, windows, all_symbols, strategy_symbols, params, lookback, db))

    return {"task_id": task_id}


# === 4. Stream progress via SSE ===
@router.get("/backtest/walkforward/stream/{task_id}")
async def stream_walkforward_progress(task_id: str):
    async def event_generator():
        last_state = {}

        while True:
            task = tasks_store.get(task_id)
            if not task:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            progress_snapshot = {
                "segments": task.get("progress", {}),
                "overall_progress": task.get("overall_progress", 0.0),
                "status": task.get("status", "unknown")
            }

            if progress_snapshot != last_state:
                last_state = progress_snapshot.copy()
                yield f"data: {json.dumps(progress_snapshot)}\n\n"

            if task["status"] == "done":
                yield f"data: {json.dumps({'done': True})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# === 5. Retrieve final aggregated results ===
@router.get("/backtest/walkforward/results/{task_id}")
def get_walkforward_aggregated_results(task_id: str):
    task = tasks_store.get(task_id)
    if not task or task["status"] != "done":
        return JSONResponse({"detail": "Task not found or not completed"}, status_code=404)

    # flatten all segment results
    segments = [task["results"][seg_id] for seg_id in sorted(task["results"].keys())]

    # compute walk-forward results
    window_length = task.get("window_length", 3)

    walkforward_results = compute_walkforward_results(segments, window_length)

    aggregated = aggregate_walkforward_results(walkforward_results)
    symbol_results = [r for r in aggregated if r["symbol"] != "overall"]
    return {
        "task_id": task_id,
        "status": task["status"],
        "aggregated_results": symbol_results
    }
