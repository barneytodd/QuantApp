# routers/optimisation.py

from fastapi import APIRouter, Depends
from app.services.backtesting.engines.param_optimiser import optimise_parameters
from app.schemas import ParamOptimisationRequest

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
