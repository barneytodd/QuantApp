import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import ParamOptimisationRequest
from app.services.backtesting.engines.param_optimiser import optimise_parameters
from app.stores.task_stores import param_optimisation_tasks_store as tasks_store


router = APIRouter()

@router.post("/optimise")
def optimise_strategy_parameters(payload: ParamOptimisationRequest):
    strategies_config = payload.strategies
    global_params = payload.globalParams
    optimisation_params = payload.optimParams
    if payload.scoringParams is not None:
        scoring_params = payload.scoringParams
    else:
        scoring_params = {
            "sharpe": 0.5,
            "cagr": 0.3,
            "max_drawdown": 0.2,
            "win_rate": 0.1
        }
    results = optimise_parameters(strategies_config, global_params, optimisation_params, scoring_params)
    return results


@router.get("/optimisation/stream")
async def stream_all_param_optimisation_progress():
    async def event_generator():
        last_state = {}

        while True:
            # collect all strategies
            if tasks_store == {}:
                await asyncio.sleep(5)
                continue
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

            # only yield if there�s an update
            if all_strategies_progress != last_state:
                last_state = all_strategies_progress.copy()
                yield f"data: {json.dumps(all_strategies_progress)}\n\n"

            # exit if all strategies done
            if all(task["status"] == "done" for task in tasks_store.values()):
                yield f"data: {json.dumps({'done': True})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
