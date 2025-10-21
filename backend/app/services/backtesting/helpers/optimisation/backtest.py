import uuid
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StrategyRequest
from app.services.backtesting.tasks.walkforward_manager import run_walkforward_async
from app.services.backtesting.helpers.data import (
    aggregate_walkforward_results,
    compute_walkforward_results,
    create_walkforward_windows,
    prepare_backtest_inputs,
)
from app.stores.task_stores import walkforward_tasks_store as tasks_store


async def run_strategy_backtest(cfg, global_params, window_length=3, db: Session = Depends(get_db)):
    """
    Run a full strategy backtest using a walk-forward approach.

    Steps:
        1. Merge symbol items and trial parameters with global parameters.
        2. Prepare inputs: flat symbol list, symbol-strategy mapping, lookback, and params.
        3. Generate rolling walk-forward windows.
        4. Execute the asynchronous walk-forward backtest.
        5. Retrieve per-window results from the task store.
        6. Compute walk-forward metrics for each segment.
        7. Aggregate results across all windows into a final summary.

    Args:
        cfg (dict): Backtest configuration including 'symbolItems' and 'trial_params'.
        global_params (dict): Global backtest parameters like capital, slippage, etc.
        window_length (int): Number of years per walk-forward segment.
        db (Session): SQLAlchemy session dependency.

    Returns:
        aggregated (list[dict]): Aggregated performance metrics for each symbol-strategy pair.
    """

    # Extract symbols and trial-specific parameters from config
    symbol_items = cfg["symbolItems"]
    strategy_params = cfg["trial_params"]

    # Merge global and strategy-specific parameters
    params = {**global_params, **strategy_params}

    # --- Prepare inputs for backtest ---
    # Returns: flat list of all symbols, mapping of unique symbol-strategy keys,
    # flattened params, and max lookback window
    all_symbols, strategy_symbols, params, lookback = prepare_backtest_inputs(StrategyRequest(
        symbolItems=symbol_items,
        params=params
    ))

    # --- Generate rolling walk-forward windows ---
    # Here, window_length=1 for yearly rolling windows
    windows = create_walkforward_windows(params["startDate"], params["endDate"], window_length=1)

    # Unique ID for tracking this backtest in the task store
    task_id = str(uuid.uuid4())

    # --- Run asynchronous walk-forward backtest ---
    # Await the async task directly instead of creating a separate task
    await run_walkforward_async(
        task_id, windows, all_symbols, strategy_symbols, params, lookback, db, window_length=window_length
    )

    # Retrieve results from the in-memory task store
    task = tasks_store[task_id]
    segments = [r for r in task["results"].values()]

    # Use walkforward window length from task metadata if available
    window_length = task.get("window_length", 3)

    # --- Compute per-segment walk-forward metrics ---
    walkforward_results = compute_walkforward_results(segments, window_length)

    # --- Aggregate metrics across all windows ---
    aggregated = aggregate_walkforward_results(walkforward_results)

    return aggregated
