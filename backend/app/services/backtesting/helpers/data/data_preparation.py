from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from collections import defaultdict



def prepare_backtest_inputs(payload):
    """
    Common setup for both standard and walk-forward backtests.
    Builds symbols mapping, flattens params, computes lookback.
    """
    if not payload.symbolItems:
        print("No symbol items in payload:", payload)
        raise ValueError("No symbols provided")
    if not payload.params:
        print("No params in payload:", payload)
        raise ValueError("No parameters provided")

    # --- Collect all symbols (flat list) ---
    individual_symbols = list({s for item in payload.symbolItems for s in item["symbols"]})

    # --- Build symbol-strategy mapping ---
    strategy_symbols = {}
    for item in payload.symbolItems:
        key_base = "-".join(item["symbols"])
        strategy = item["strategy"]
        key = f"{key_base}_{strategy}"  # Unique key per symbol-strategy pair
        print( "Mapping key:", key)
        strategy_symbols[key] = {
            "symbol": key_base,   # e.g. "AAPL" or "AAPL-MSFT"
            "strategy": strategy,
            "weight": item.get("weight", 1),
        }

    # --- Compute lookback window ---
    print( "Params:", payload.params)
    max_lookback = max(
        (v["value"] for k, v in payload.params.items() if v.get("lookback")), default=0
    )


    params = {p: v["value"] for p, v in payload.params.items()}

    return individual_symbols, strategy_symbols, params, max_lookback


def create_walkforward_windows(start_date: str, end_date: str, window_length: int):
    """Generate rolling walk-forward training/testing windows."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    windows = []
    current_start = start
    while current_start + relativedelta(years=window_length) <= end + relativedelta(days=1):
        current_end = min(current_start + relativedelta(years=window_length), end)
        windows.append({
            "start": current_start.strftime("%Y-%m-%d"),
            "end": current_end.strftime("%Y-%m-%d"),
        })
        current_start += relativedelta(years=1)
    return windows


