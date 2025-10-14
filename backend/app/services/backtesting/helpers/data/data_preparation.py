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

        strategy_symbols[key] = {
            "symbol": key_base,   # e.g. "AAPL" or "AAPL-MSFT"
            "strategy": strategy,
            "weight": item.get("weight", 1),
        }

    # --- Compute lookback window ---
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


import numpy as np
from collections import defaultdict

def aggregate_walkforward_results(segment_results):
    """
    Aggregate performance metrics per (symbol, strategy),
    ignoring segments with no trades.
    """
    metrics_per_pair = defaultdict(lambda: {
        "sharpe": [],
        "cagr": [],
        "maxDrawdown": [],
        "winRate": [],
        "no_trade_segments": 0,
    })

    for segment in segment_results:
        for strat_result in segment:
            symbol = strat_result.get("symbol")
            strategy = strat_result.get("strategy")
            pair_key = (symbol, strategy)

            metrics = strat_result.get("metrics") or {}
            trade_stats = strat_result.get("tradeStats") or {}

            # if no trades, count it and skip from averages
            if strat_result.get("tradeStats") is None or not strat_result.get("trades"):
                metrics_per_pair[pair_key]["no_trade_segments"] += 1
                continue

            # Only aggregate if trades exist
            if "sharpe" in metrics and metrics["sharpe"] is not None:
                metrics_per_pair[pair_key]["sharpe"].append(metrics["sharpe"])
            if "cagr" in metrics and metrics["cagr"] is not None:
                metrics_per_pair[pair_key]["cagr"].append(metrics["cagr"])
            if "maxDrawdown" in metrics and metrics["maxDrawdown"] is not None:
                metrics_per_pair[pair_key]["maxDrawdown"].append(metrics["maxDrawdown"])
            if "winRate" in trade_stats and trade_stats["winRate"] is not None:
                metrics_per_pair[pair_key]["winRate"].append(trade_stats["winRate"])

    def safe_mean(values):
        return float(np.mean(values)) if values else None

    aggregated = []
    for (symbol, strategy), vals in metrics_per_pair.items():
        active_segments = len(segment_results) - vals["no_trade_segments"]
        aggregated.append({
            "symbol": symbol,
            "strategy": strategy,
            "segments": len(segment_results),
            "activeSegments": active_segments,
            "noTradeSegments": vals["no_trade_segments"],
            "avgSharpe": safe_mean(vals["sharpe"]),
            "avgCAGR": safe_mean(vals["cagr"]),
            "avgMaxDrawdown": safe_mean(vals["maxDrawdown"]),
            "avgWinRate": safe_mean(vals["winRate"]),
        })

    return aggregated

