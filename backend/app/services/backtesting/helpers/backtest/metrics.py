from math import sqrt

# Compute daily returns from equity curve
def compute_daily_returns(equity_curve):
    returns = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i-1]["value"]
        curr = equity_curve[i]["value"]
        returns.append((curr - prev) / prev)
    return returns

# Compute financial metrics from equity curve
def compute_metrics(equity_curve, risk_free_rate=0.01):
    returns = compute_daily_returns(equity_curve)
    if not returns:
        return None

    n = len(returns)
    mean_daily = sum(returns) / n
    variance = sum((r - mean_daily)**2 for r in returns) / n
    std_daily = sqrt(variance)

    trading_days = 252
    mean_annual = mean_daily * trading_days
    vol_annual = std_daily * sqrt(trading_days)
    sharpe = (mean_annual - risk_free_rate) / vol_annual if vol_annual > 0 else 0

    peak = equity_curve[0]["value"]
    max_drawdown = 0
    for point in equity_curve:
        peak = max(peak, point["value"])
        drawdown = (peak - point["value"]) / peak
        max_drawdown = max(max_drawdown, drawdown)

    return {
        "mean_return": mean_annual,
        "annualised_volatility": vol_annual,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown * 100
    }

# Compute trade statistics from list of trades
def compute_trade_stats(trades):
    if not trades:
        return None

    wins = [t for t in trades if t["returnPct"] > 0]
    losses = [t for t in trades if t["returnPct"] <= 0]

    total_win = sum(t["returnPct"]/100 * t["entryPrice"] for t in wins)
    total_loss = sum(abs(t["returnPct"]/100 * t["entryPrice"]) for t in losses)

    return {
        "numTrades": len(trades),
        "winRate": len(wins)/len(trades)*100 if trades else None,
        "avgWin": total_win/len(wins) if wins else 0,
        "avgLoss": -total_loss/len(losses) if losses else 0,
        "profitFactor": total_win/total_loss if total_loss > 0 else None,
        "bestTrade": max(trades, key=lambda x: x["pnl"]),
        "worstTrade": min(trades, key=lambda x: x["pnl"])
    }