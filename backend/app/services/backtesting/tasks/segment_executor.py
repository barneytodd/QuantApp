from app.services.backtesting.engines.backtest_engine import run_backtest

def run_segment(segment_id, data, strategy_symbols, params, progress_state):
    """
    Run a single backtest segment and update a shared progress state.

    Args:
        segment_id (int or str): Unique identifier for this segment.
        data (dict): Historical price data for all symbols.
        strategy_symbols (dict): Mapping of symbol-strategy keys to their info.
        params (dict): Global and strategy-specific parameters.
        lookback (int): Number of initial bars to skip in the backtest.
        progress_state (dict): Shared dict to track segment progress and results.

    Returns:
        list: Backtest results for this segment.
    """

    # --- Callback for progress updates during backtest ---
    def progress_callback(current_idx, total):
        # Calculate percentage complete
        pct = round(current_idx / total * 100, 2)
        # Update shared progress state for this segment
        progress_state["segments"][segment_id]["progress_pct"] = pct

    # --- Run the actual backtest ---
    result = run_backtest(
        data,
        strategy_symbols,
        params,
        progress_callback  # Pass callback to track progress per date
    )

    # --- Update segment state after completion ---
    seg_state = progress_state["segments"][segment_id]
    seg_state["progress_pct"] = 100.0
    seg_state["done"] = True

    # --- Store the backtest result in the shared results dict ---
    progress_state["results"][segment_id] = result

    return result
