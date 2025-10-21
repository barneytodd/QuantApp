import asyncio

from app.services.backtesting.engines.pairs_selection import analyze_pairs
from app.stores.task_stores import pairs_tasks_store as tasks_store
from app.services.backtesting.helpers.pairs.pair_selection import select_pairs_max_weight


# === Background worker ===
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



# === Async listener for progress ===
async def monitor_pair_selection_progress(task_id: str, progress_state):
    """Poll the shared progress dict periodically and mirror to tasks_store."""
    tasks_store[task_id] = dict(progress_state)

    while True:
        # Copy current state into local store
        tasks_store[task_id] = dict(progress_state)

        if progress_state.get("status") in ("done", "failed"):
            break

        await asyncio.sleep(0.2)