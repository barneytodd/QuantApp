import uuid

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StrategyRequest
from app.api.routes.backtesting.backtest import run_walkforward_async
from app.services.backtesting.helpers.data import (
    aggregate_walkforward_results,
    compute_walkforward_results,
    create_walkforward_windows,
    prepare_backtest_inputs,
)
from app.stores.task_stores import walkforward_tasks_store as tasks_store



async def run_strategy_backtest(cfg, global_params, window_length=3, db: Session = Depends(get_db)):
    # Generate trial params

    symbol_items = cfg["symbolItems"]
    strategy_params = cfg["trial_params"]

    params = {**global_params, **strategy_params}

    # Prepare and run walkforward directly
    all_symbols, strategy_symbols, params, lookback = prepare_backtest_inputs(StrategyRequest(
        symbolItems = symbol_items,
        params = params
    ))

    windows = create_walkforward_windows(params["startDate"], params["endDate"], window_length=1)
    task_id = str(uuid.uuid4())
    # Instead of create_task -> await directly
    await run_walkforward_async(
        task_id, windows, all_symbols, strategy_symbols, params, lookback, db, window_length=window_length
    )

    task = tasks_store[task_id]
    segments = [r for r in task["results"].values()]
    
    window_length = task.get("window_length", 3)
    walkforward_results = compute_walkforward_results(segments, window_length)
    aggregated = aggregate_walkforward_results(walkforward_results)

    return aggregated
