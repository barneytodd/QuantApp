import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import ParamOptimisationRequest
from app.services.backtesting.engines.param_optimiser import optimise_parameters
from app.stores.task_stores import param_optimisation_tasks_store as tasks_store

router = APIRouter()


# === Run parameter optimisation for one or multiple strategies ===
@router.post("/optimise")
def optimise_strategy_parameters(payload: ParamOptimisationRequest):
    """
    Start a parameter optimisation for given strategies.

    Steps:
    1. Extract strategy-specific and global parameters from payload.
    2. Use default scoring weights if none are provided.
    3. Call `optimise_parameters` to run optimisation for all strategies.
    4. Return the results dictionary containing best parameters and scores per strategy.

    Scoring weights (if not provided) default to:
        - sharpe: 0.5
        - cagr: 0.3
        - max_drawdown: 0.2
        - win_rate: 0.1
    """
    strategies_config = payload.strategies
    global_params = payload.globalParams
    optimisation_params = payload.optimParams
    scoring_params = payload.scoringParams or {
        "sharpe": 0.5,
        "cagr": 0.3,
        "max_drawdown": 0.2,
        "win_rate": 0.1
    }

    results = optimise_parameters(strategies_config, global_params, optimisation_params, scoring_params)
    return results


# === Stream real-time progress of parameter optimisation via SSE ===
@router.get("/optimisation/stream")
async def stream_all_param_optimisation_progress():
    """
    Stream live progress updates for all ongoing parameter optimisation tasks.

    Returns a JSON object per strategy containing:
        - completed_trials: number of trials finished
        - total_trials: total trials scheduled
        - status: current task status ("running", "done", etc.)
        - best_score: best scoring value so far
        - best_params: parameter combination achieving best score

    When all strategies are finished, yields {"done": True} and closes the stream.
    """
    async def event_generator():
        last_state = {}

        while True:
            if not tasks_store:
                # Wait if no tasks have started yet
                await asyncio.sleep(5)
                continue

            # Gather progress per strategy
            all_strategies_progress = {
                strategy_name: {
                    "completed_trials": task["completed_trials"],
                    "total_trials": task["total_trials"],
                    "status": task["status"],
                    "best_score": task["best_score"],
                    "best_params": task["best_params"],
                }
                for strategy_name, task in tasks_store.items()
            }

            # Only send update if there is a change
            if all_strategies_progress != last_state:
                last_state = all_strategies_progress.copy()
                yield f"data: {json.dumps(all_strategies_progress)}\n\n"

            # Stop streaming once all strategies are done
            if all(task["status"] == "done" for task in tasks_store.values()):
                yield f"data: {json.dumps({'done': True})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
