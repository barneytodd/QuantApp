from collections import defaultdict
import numpy as np
import pandas as pd

from ..backtest.metrics import compute_metrics, compute_trade_stats


def compute_walkforward_results(results, window_length):
    """
    Compute walkforward results from individual segment results.
    Aggregates equity curves, trades, and metrics across rolling windows.

    Args:
        results (list): list of backtest results per segment
        window_length (int): number of segments to include in each walkforward window

    Returns:
        list: aggregated segment results per window
    """
    if not results: 
        return None

    start = 0
    walkforward_results = []

    # Loop over rolling windows
    while start + window_length <= len(results):
        # Initialize tracking dictionaries for this window
        initial_capitals = {}  # stores capital per symbol
        equity_curves = {}     # stores equity curves per symbol
        strategies = {}        # symbol -> strategy mapping
        trades = {}            # trades per symbol
        wins = 0               # track winning trades
        total_trades = 0       # track total trades

        # Aggregate segments within the window
        for i in range(start, start+window_length):
            for idx, strat_result in enumerate(results[i]):
                symbol = strat_result.get("symbol")
                strategy = strat_result.get("strategy")
                strategies[symbol] = strategy

                assumed_initial_capital = strat_result.get("initialCapital")

                # Scale equity curve based on prior final capital
                equity_curve = [
                    {
                        "date": item["date"], 
                        "value": item["value"] * initial_capitals.get(symbol, assumed_initial_capital) / assumed_initial_capital
                    }
                    for item in strat_result.get("equityCurve") if item["value"] is not None
                ]
                equity_curves.setdefault(symbol, []).extend(equity_curve)

                # Update capital for next segment
                if strat_result["finalCapital"] is not None:
                    initial_capitals[symbol] = strat_result["finalCapital"]

                # Aggregate trades
                trades.setdefault(symbol, []).extend(strat_result.get("trades", []))

                # Count wins for computing win rate
                trade_stats = strat_result["tradeStats"]
                if trade_stats:
                    wins += strat_result["tradeStats"]["winRate"] * strat_result["tradeStats"]["numTrades"] / 100
                    total_trades += strat_result["tradeStats"]["numTrades"]
        
        # Compute metrics and trade stats for each symbol in the window
        segment_result = []
        for symbol, strategy in strategies.items():
            metrics = compute_metrics(equity_curves[symbol])
            trade_stats = compute_trade_stats(trades[symbol])
            segment_result.append({
                "symbol": symbol,
                "strategy": strategy,
                "equity_curve": equity_curves[symbol],
                "trades": trades[symbol],
                "metrics": metrics,
                "tradeStats": trade_stats
            })
        walkforward_results.append(segment_result)
        start += 1

    return walkforward_results


def aggregate_walkforward_results(segment_results):
    """
    Aggregate performance metrics per (symbol, strategy),
    ignoring segments with no trades.

    Args:
        segment_results (list): walkforward segment results

    Returns:
        list: aggregated results per symbol-strategy pair
    """
    # Prepare dictionary to accumulate metrics
    metrics_per_pair = defaultdict(lambda: {
        "sharpe": [],
        "cagr": [],
        "maxDrawdown": [],
        "winRate": [],
        "no_trade_segments": 0,
        "complete_equity_curve": []
    })

    # Iterate through each walkforward segment
    for segment in segment_results:
        for strat_result in segment:
            symbol = strat_result.get("symbol")
            strategy = strat_result.get("strategy")
            pair_key = (symbol, strategy)

            metrics = strat_result.get("metrics") or {}
            trade_stats = strat_result.get("tradeStats") or {}

            # Skip segments with no trades, increment no_trade counter
            if strat_result.get("tradeStats") is None or not strat_result.get("trades"):
                metrics_per_pair[pair_key]["no_trade_segments"] += 1
                continue

            # Aggregate available metrics
            if "sharpe_ratio" in metrics and metrics["sharpe_ratio"] is not None:
                metrics_per_pair[pair_key]["sharpe"].append(metrics["sharpe_ratio"])
            if "cagr" in metrics and metrics["cagr"] is not None:
                metrics_per_pair[pair_key]["cagr"].append(metrics["cagr"])
            if "max_drawdown" in metrics and metrics["max_drawdown"] is not None:
                metrics_per_pair[pair_key]["maxDrawdown"].append(metrics["max_drawdown"])
            if "winRate" in trade_stats and trade_stats["winRate"] is not None:
                metrics_per_pair[pair_key]["winRate"].append(trade_stats["winRate"])
            if "equity_curve" in strat_result and strat_result["equity_curve"] is not None:
                metrics_per_pair[pair_key]["complete_equity_curve"].extend(strat_result["equity_curve"])

    # Helper function to safely compute mean
    def safe_mean(values):
        return float(np.mean(values)) if values else None

    # Helper function to compute daily returns from combined equity curve
    def compute_returns(equity_curve):
        if not equity_curve:
            return None
        df = pd.DataFrame(equity_curve).sort_values("date")
        df = df.drop_duplicates(subset="date", keep="first")
        df["return"] = df["value"].pct_change(fill_method=None)
        df = df.dropna(subset=["return"])
        return df.to_dict(orient="records")

    # Build final aggregated results per symbol-strategy
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
            "returns": compute_returns(vals["complete_equity_curve"])
        })
        
    return aggregated
