from app.database import SessionLocal
import asyncio, uuid
from app.schemas import StrategyRequest

from app.api.routes.backtest import run_walkforward_async
from app.tasks import walkforward_tasks_store as tasks_store
from app.services.backtesting.helpers.data.data_preparation import prepare_backtest_inputs, create_walkforward_windows
from app.services.backtesting.helpers.data.data_aggregation import compute_walkforward_results, aggregate_walkforward_results


async def run_strategy_backtest(cfg, global_params, window_length=3):
    # Generate trial params
    db = SessionLocal()

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
        
    overall_results = [r for r in aggregated if r["symbol"] == "overall"]    

    return overall_results
