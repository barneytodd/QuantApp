from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue, Process
import json, asyncio, os, uuid

from app.database import get_db
from app.schemas import StrategyRequest
from app.services.backtesting.helpers.data.data_preparation import (
    prepare_backtest_inputs,
    create_walkforward_windows,
    aggregate_walkforward_results,
)
from app.services.backtesting.tasks.tasks import run_segment
from app.services.backtesting.engines.backtest_engine import run_backtest
from app.utils.data_helpers import fetch_price_data
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
async def run_walkforward_async(task_id, windows, all_symbols, strategy_symbols, params, lookback, db):
    """
    Run walk-forward segments in parallel and update tasks_store
    by listening to a multiprocessing.Queue for live progress updates.
    """
    import os
    from app.tasks import walkforward_tasks_store as tasks_store
    from app.services.backtesting.engines.backtest_engine import run_backtest

    tasks_store[task_id] = {
        "progress": {},
        "results": {},
        "status": "running",
        "overall_progress": 0.0,
        "total_segments": len(windows),
    }

    progress_queue = Queue()  # multiprocessing queue for progress

    # Start all segment processes
    processes = []
    for seg_id, window in enumerate(windows, start=1):
        # Fetch segment data
        data = fetch_price_data(db, all_symbols, window["start"], window["end"], lookback)

        p = Process(
            target=run_segment,
            args=(data, seg_id, strategy_symbols, params, lookback, progress_queue)
        )
        p.start()
        processes.append(p)

        # Initialize progress
        tasks_store[task_id]["progress"][seg_id] = {
            "progress_pct": 0.0,
            "done": False
        }

    # Listen to the queue asynchronously
    loop = asyncio.get_running_loop()
    completed_segments = set()
    total_segments = len(windows)

    while len(completed_segments) < total_segments:
        # Use run_in_executor to read from the blocking queue without blocking the event loop
        msg = await loop.run_in_executor(None, progress_queue.get)

        seg_id = msg["segment_id"]
        tasks_store[task_id]["progress"][seg_id]["progress_pct"] = msg["progress_pct"]
        tasks_store[task_id]["progress"][seg_id]["done"] = msg["done"]

        # If result is included, store it
        if msg.get("result") is not None:
            tasks_store[task_id]["results"][seg_id] = msg["result"]

        if msg["done"]:
            completed_segments.add(seg_id)
            print(f"[{task_id}] Segment {seg_id} completed.")

        # Update overall progress
        overall = sum(v["progress_pct"] for v in tasks_store[task_id]["progress"].values()) / total_segments
        tasks_store[task_id]["overall_progress"] = overall

        await asyncio.sleep(0.01)  # small sleep to avoid busy-loop

    # Wait for all processes to exit
    for p in processes:
        p.join()

    tasks_store[task_id]["status"] = "done"
    print(f"[{task_id}] Walk-forward backtest completed.")


# === 3. Launch walkforward task ===
@router.post("/backtest/walkforward/start")
def start_walkforward_backtest(
    payload: StrategyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        all_symbols, strategy_symbols, params, lookback = prepare_backtest_inputs(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    windows = create_walkforward_windows(params["startDate"], params["endDate"], window_length=3)
    if not windows:
        raise HTTPException(status_code=400, detail="Invalid walk-forward configuration")

    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {
        "progress": {},
        "results": {},
        "status": "pending",
        "overall_progress": 0.0,
        "total_segments": len(windows)
    }

    # Launch async walkforward execution in background
    async def task_wrapper():
        await run_walkforward_async(task_id, windows, all_symbols, strategy_symbols, params, lookback, db)

    background_tasks.add_task(asyncio.run, task_wrapper())
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

    aggregated = aggregate_walkforward_results(segments)
    return {
        "task_id": task_id,
        "status": task["status"],
        "aggregated_results": aggregated
    }
