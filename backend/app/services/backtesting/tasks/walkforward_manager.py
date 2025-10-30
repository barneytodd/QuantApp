import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from app.database import SessionLocal
from app.services.backtesting.tasks.segment_executor import run_segment
from app.stores.task_stores import walkforward_tasks_store as tasks_store
from app.utils.data_helpers import fetch_price_data_light

# === Walkforward async engine ===
async def run_walkforward_async(
    task_id, windows, all_symbols, strategy_symbols, params, lookback, window_length=3
):
    """
    Run a walk-forward backtest across multiple time windows in parallel.
    Progress is tracked in a shared dictionary and mirrored to tasks_store for monitoring.

    Args:
        task_id: unique task identifier
        windows: list of training/testing windows
        all_symbols: list of all symbols used in backtest
        strategy_symbols: dict mapping symbol-strategy keys to configs
        params: global and strategy-specific parameters
        lookback: initial bars to skip
        window_length: number of years in each window
    """

    # --- Create shared state with multiprocessing Manager ---
    manager = Manager()
    progress_state = manager.dict()
    progress_state["segments"] = manager.dict()       # per-segment progress
    progress_state["results"] = manager.dict()        # per-segment results
    progress_state["overall_progress"] = 0.0
    progress_state["done_segments"] = 0

    # --- Initialize task entry in the global store ---
    tasks_store[task_id] = {
        "status": "running",
        "progress": {},
        "overall_progress": 0.0,
        "results": {},
        "total_segments": len(windows),
        "window_length": window_length
    }

    # --- Initialize per-segment progress ---
    for seg_id, window in enumerate(windows, start=1):
        progress_state["segments"][seg_id] = manager.dict(progress_pct=0.0, done=False)

    # --- Start async listener to mirror progress_state into tasks_store ---
    asyncio.create_task(sync_progress_state_to_store(task_id, progress_state))

    # --- Run backtest segments in parallel using process pool ---
    max_workers = max(1, (os.cpu_count() or 4) - 1)
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        loop = asyncio.get_running_loop()
        tasks = []

        for seg_id, window in enumerate(windows, start=1):
            # Submit segment execution to process pool
            tasks.append(loop.run_in_executor(
                pool,
                run_segment_with_data_fetch,
                seg_id, all_symbols, strategy_symbols, params, lookback, progress_state, window["start"], window["end"]
            ))

        # Await completion of all segment backtests
        await asyncio.gather(*tasks)

    # --- Finalize task state after all segments complete ---
    progress_state["done_segments"] = len(windows)
    progress_state["overall_progress"] = 100.0
    tasks_store[task_id]["status"] = "done"

def run_segment_with_data_fetch(segment_id, all_symbols, strategy_symbols, params, lookback, progress_state, start, end):
    """Worker: fetch data and run one segment inside its own process."""
    db = SessionLocal()
    try:
        data = fetch_price_data_light(db, all_symbols, start, end, lookback)
        result = run_segment(segment_id, data, strategy_symbols, params, lookback, progress_state)
    except Exception as e:
        print(e)
    finally:
        db.close()


async def sync_progress_state_to_store(task_id, progress_state):
    """
    Continuously mirror the Manager dictionary into tasks_store.

    Allows external APIs or UIs to monitor backtest progress in near real-time.
    """
    while tasks_store[task_id]["status"] == "running":
        total_segments = len(progress_state["segments"])
        if total_segments == 0:
            await asyncio.sleep(0.2)
            continue

        # --- Compute aggregate progress across all segments ---
        overall = sum(seg["progress_pct"] for seg in progress_state["segments"].values()) / total_segments
        tasks_store[task_id]["overall_progress"] = overall

        # --- Mirror per-segment progress ---
        for seg_id, seg_data in progress_state["segments"].items():
            tasks_store[task_id]["progress"][seg_id] = {
                "progress_pct": seg_data["progress_pct"],
                "done": seg_data["done"],
            }

        # --- Mirror segment results as they arrive ---
        for seg_id, result in progress_state["results"].items():
            tasks_store[task_id]["results"][seg_id] = result

        await asyncio.sleep(0.3)
