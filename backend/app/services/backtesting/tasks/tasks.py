from app.services.backtesting.engines.backtest_engine import run_backtest

def run_segment(segment_id, data, strategy_symbols, params, lookback, progress_state):
    """Run one backtest segment and update shared progress_state directly."""

    def progress_callback(current_idx, total):
        pct = round(current_idx / total * 100, 2)
        progress_state["segments"][segment_id]["progress_pct"] = pct

    # Run backtest and get result
    result = run_backtest(data, strategy_symbols, params, lookback, progress_callback)

    # Update final segment state
    seg_state = progress_state["segments"][segment_id]
    seg_state["progress_pct"] = 100.0
    seg_state["done"] = True

    # Store result in shared dict
    progress_state["results"][segment_id] = result

    return result
