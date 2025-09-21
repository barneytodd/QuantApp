from math import sqrt
from collections import defaultdict

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

# Calculate commission costs
def commission(signal="buy", capital=0, effective_price=0, position=0, commission_pct=0.001, commission_fixed=0.0):
    if signal == "buy":
        return (capital * commission_pct + commission_fixed * effective_price) / (effective_price + commission_pct)
    else:
        return position * commission_pct + commission_fixed

# Run backtest on historical data with given parameters and signal generator
def run_backtest(data, params, signal_generator, initial_capital=10000, slippage_pct=0.0005):
    symbol = data[0]["symbol"]
    capital = initial_capital
    position = 0
    equity_curve = []
    trades = []
    entry_price = None
    entry_date = None
    for i, row in enumerate(data):
        price = row["close"]
        signal = signal_generator(data, i, params)

        if signal == "buy" and position == 0:
            effective_price = price * (1 + slippage_pct)
            position = (capital - commission(signal, capital, effective_price, 0)) / effective_price
            capital = 0
            entry_price = price
            entry_date = row["date"]

        if signal == "sell" and position > 0:
            effective_exit = price * (1 - slippage_pct)
            effective_entry = entry_price * (1 + slippage_pct)
            pnl = position * (effective_exit - effective_entry)
            return_pct = (effective_exit - effective_entry) / effective_entry * 100
            trades.append({
                "symbol": symbol,
                "entryDate": entry_date,
                "exitDate": row["date"],
                "entryPrice": entry_price,
                "exitPrice": price,
                "pnl": pnl,
                "returnPct": return_pct
            })
            capital = position * effective_exit - commission("sell", 0, 0, position)
            position = 0
            entry_price = None
            entry_date = None

        equity_curve.append({"date": row["date"], "value": capital + position * price})

    # Final liquidation
    if position > 0:
        last_price = data[-1]["close"]
        effective_last = last_price * (1 - slippage_pct)
        effective_entry = entry_price * (1 + slippage_pct)
        pnl = position * (effective_last - effective_entry)
        return_pct = (effective_last - effective_entry) / effective_entry * 100
        trades.append({
            "symbol": symbol,
            "entryDate": entry_date,
            "exitDate": data[-1]["date"],
            "entryPrice": entry_price,
            "exitPrice": last_price,
            "pnl": pnl,
            "returnPct": return_pct
        })
        capital = position * last_price - commission("sell", 0, 0, position)
        position = 0
    return {
        "symbol": symbol,
        "initialCapital": initial_capital,
        "finalCapital": capital,
        "returnPct": (capital / initial_capital - 1) * 100,
        "equityCurve": equity_curve,
        "trades": trades,
        "metrics": compute_metrics(equity_curve),
        "tradeStats": compute_trade_stats(trades)
    }

# Combine results from multiple backtests into one overall result
def combine_results(results):

    date_map = defaultdict(float)
    combined_trades = []

    all_dates = sorted({p["date"] for r in results for p in r["equityCurve"]})

    for r in results:

        curve = r["equityCurve"]
        idx = 0
        n = len(curve)
        last_value = r["initialCapital"]

        for date in all_dates:
            while idx < n and curve[idx]["date"] <= date:
                last_value = curve[idx]["value"]
                idx += 1
            value = last_value
            date_map[date] += value

        combined_trades.extend(r["trades"])

    combined_curve = [{"date": date, "value": value} for date, value in sorted(date_map.items())]
    initial_capital = sum(r["initialCapital"] for r in results)
    final_capital = combined_curve[-1]["value"] if combined_curve else initial_capital
    return {
        "symbol": "overall",
        "initialCapital": initial_capital,
        "finalCapital": final_capital,
        "returnPct": (final_capital / initial_capital - 1) * 100,
        "equityCurve": combined_curve,
        "trades": combined_trades,
        "metrics": compute_metrics(combined_curve),
        "tradeStats": compute_trade_stats(combined_trades)
    }
