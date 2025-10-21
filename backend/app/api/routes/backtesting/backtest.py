import asyncio
import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StrategyRequest
from app.services.backtesting.engines.backtest_engine import run_backtest
from app.services.backtesting.helpers.data import (
    aggregate_walkforward_results, compute_walkforward_results,
    create_walkforward_windows, prepare_backtest_inputs,
)
from app.services.backtesting.tasks.walkforward_manager import run_walkforward_async
from app.stores.task_stores import walkforward_tasks_store as tasks_store
from app.utils.data_helpers import fetch_price_data


router = APIRouter()


# === Standard full-period backtest ===
@router.post("/backtest")
def run_standard_backtest(payload: StrategyRequest, db: Session = Depends(get_db)):
    """
    Run a standard backtest over the full period specified in the payload.
    
    Steps:
    1. Prepare input data (symbols, parameters, lookback) using shared helper.
    2. Fetch OHLCV price data from the database.
    3. Run backtest engine on the prepared data.
    4. Return results per symbol.
    """
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


# === Launch asynchronous walk-forward backtest task ===
@router.post("/backtest/walkforward/start")
async def start_walkforward_backtest(
    payload: StrategyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a walk-forward backtest asynchronously.
    
    Steps:
    1. Prepare input data (symbols, parameters, lookback).
    2. Create rolling windows for walk-forward testing.
    3. Register a new task in the walkforward task store with initial progress.
    4. Launch the async backtest in the background.
    5. Return task_id for tracking progress.
    """
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
        "progress": {},             # Track progress per segment
        "results": {},              # Store individual segment results
        "status": "pending",        # Task status: pending, running, done
        "overall_progress": 0.0,    # Overall progress 0.0–1.0
        "total_segments": len(windows),
        "window_length": window_length
    }

    # Launch async walkforward execution in background
    asyncio.create_task(run_walkforward_async(task_id, windows, all_symbols, strategy_symbols, params, lookback, db))

    return {"task_id": task_id}


# === Stream walk-forward task progress via Server-Sent Events (SSE) ===
@router.get("/backtest/walkforward/stream/{task_id}")
async def stream_walkforward_progress(task_id: str):
    """
    Stream real-time progress updates of a walk-forward backtest task.
    
    Returns:
        SSE stream of JSON objects with:
        - segments progress
        - overall_progress (0–1)
        - status (pending/running/done)
        - done=True when finished
    """
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

            # Yield update only if there is a change
            if progress_snapshot != last_state:
                last_state = progress_snapshot.copy()
                yield f"data: {json.dumps(progress_snapshot)}\n\n"

            if task["status"] == "done":
                yield f"data: {json.dumps({'done': True})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# === Retrieve aggregated walk-forward results ===
@router.get("/backtest/walkforward/results/{task_id}")
def get_walkforward_aggregated_results(task_id: str):
    """
    Retrieve final aggregated results of a completed walk-forward backtest task.
    
    Steps:
    1. Validate task exists and is completed.
    2. Flatten results from all segments.
    3. Compute walk-forward metrics per symbol and overall.
    4. Return aggregated results.
    """
    task = tasks_store.get(task_id)
    if not task or task["status"] != "done":
        return JSONResponse({"detail": "Task not found or not completed"}, status_code=404)

    # Flatten all segment results
    segments = [task["results"][seg_id] for seg_id in sorted(task["results"].keys())]

    # Compute walk-forward results
    window_length = task.get("window_length", 3)
    walkforward_results = compute_walkforward_results(segments, window_length)
    aggregated = aggregate_walkforward_results(walkforward_results)

    symbol_results = [r for r in aggregated if r["symbol"] != "overall"]
    return {
        "task_id": task_id,
        "status": task["status"],
        "aggregated_results": symbol_results
    }
