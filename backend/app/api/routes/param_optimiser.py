# routers/optimisation.py

from fastapi import APIRouter, Depends
from app.services.backtesting.engines.param_optimiser import optimise_parameters
from app.schemas import ParamOptimisationRequest

router = APIRouter()

@router.post("/optimise")
def optimise_multi_strategy(payload: ParamOptimisationRequest):
    strategies_config = payload.strategies
    global_params = payload.globalParams
    optimisation_params = payload.optimParams
    results = optimise_parameters(strategies_config, global_params, optimisation_params)
    return results
