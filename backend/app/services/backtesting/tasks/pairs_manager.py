import asyncio

from fastapi import HTTPException

from app.services.backtesting.engines.pairs_selection import analyze_pairs
from app.stores.task_stores import pairs_tasks_store as tasks_store
from app.services.backtesting.helpers.pairs.pair_selection import select_pairs_max_weight


# === Background worker ===
def run_pair_selection_task(task_id, symbols, prices_dict, w_corr, w_coint, progress_state):
    """
    Run a pair selection task in the background.

    Args:
        task_id (str): Unique ID for this task.
        symbols (list): List of symbols to analyze.
        prices_dict (dict): Historical price data for each symbol.
        w_corr (float): Weight for correlation in pair scoring.
        w_coint (float): Weight for cointegration in pair scoring.
        progress_state (dict): Shared dict to track task progress and results.
    """

    # Callback to update progress during pair analysis
    def progress_callback(done, total):
        progress_state["done"] = done
        progress_state["total"] = total
        progress_state["status"] = "running"

    try:
        # --- 1. Analyze all possible pairs ---
        pairs = analyze_pairs(
            symbols,
            prices_dict,
            w_corr=w_corr,
            w_coint=w_coint,
            progress_callback=progress_callback,
        )

        # --- 2. Select best pairs using max-weight matching ---
        selected = select_pairs_max_weight(pairs, weight_key="score")

        # --- 3. Update progress state with results ---
        progress_state.update({
            "done": len(pairs),
            "total": len(pairs),
            "status": "done",
            "results": {"all_pairs": pairs, "selected_pairs": selected},
            "error": ""
        })
    except Exception as e:
        # Mark failure and store error message
        progress_state.update({"status": "failed", "error": str(e)})


# === Async listener for progress ===
async def monitor_pair_selection_progress(task_id: str, progress_state):
    """
    Asynchronous monitor that periodically copies the shared progress
    into the global tasks_store for frontend/API visibility.

    Args:
        task_id (str): Unique ID for the task being monitored.
        progress_state (dict): Shared dict updated by the worker.
    """
    # Initialize store entry
    tasks_store[task_id] = dict(progress_state)

    while True:
        # Mirror the latest progress to the store
        tasks_store[task_id] = dict(progress_state)

        # Exit once task completes or fails
        if progress_state.get("status") == "done":
            break

        if progress_state.get("status") == "failed":
            err_msg = progress_state.get("error")
            raise HTTPException(status_code=400, detail=str(err_msg))

        # Poll every 0.2 seconds
        await asyncio.sleep(0.2)
