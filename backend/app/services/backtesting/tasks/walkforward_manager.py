import asyncio
import os

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from app.services.backtesting.tasks.segment_executor import run_segment
from app.stores.task_stores import walkforward_tasks_store as tasks_store
from app.utils.data_helpers import fetch_price_data_light

# === Walkforward async engine ===
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
