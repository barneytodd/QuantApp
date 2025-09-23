from math import sqrt
from collections import defaultdict
from app.utils.backtest_helpers import compute_metrics, compute_trade_stats, commission, calc_effective_price

# Run backtest on historical data with given parameters and signal generator
def run_backtest(data, params, signal_generator, initial_capital):
    slippage_pct = params["slippage"] / 100
    transaction_pct = params["transactionCostPct"] / 100
    transaction_fixed = params["fixedTransactionCost"] 
    
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
            effective_price = calc_effective_price(price, slippage_pct, "buy")
            position = (capital - commission(signal, capital, effective_price, 0, transaction_pct,transaction_fixed)) / effective_price
            capital = 0
            entry_price = price
            entry_date = row["date"]

        if signal == "sell" and position > 0:
            effective_exit = calc_effective_price(price, slippage_pct, "sell")
            effective_entry = calc_effective_price(entry_price, slippage_pct, "buy")
            pnl = position * (effective_exit - effective_entry)
            return_pct = (effective_exit - effective_entry) / effective_entry * 100
            trades.append({
                "symbol": symbol,
                "direction": "Long",
                "entryDate": entry_date,
                "exitDate": row["date"],
                "entryPrice": entry_price,
                "exitPrice": price,
                "pnl": pnl,
                "returnPct": return_pct
            })
            capital = position * effective_exit - commission("sell", 0, effective_exit, position, transaction_pct,transaction_fixed)
            position = 0
            entry_price = None
            entry_date = None

        equity_curve.append({"date": row["date"], "value": capital + position * price})

    # Final liquidation
    if position > 0:
        last_price = data[-1]["close"]
        effective_last = calc_effective_price(last_price, slippage_pct, "sell")
        effective_entry = calc_effective_price(entry_price, slippage_pct, "buy")
        pnl = position * (effective_last - effective_entry)
        return_pct = (effective_last - effective_entry) / effective_entry * 100
        trades.append({
            "symbol": symbol,
            "direction": "Long",
            "entryDate": entry_date,
            "exitDate": data[-1]["date"],
            "entryPrice": entry_price,
            "exitPrice": last_price,
            "pnl": pnl,
            "returnPct": return_pct
        })
        capital = position * last_price - commission("sell", 0, effective_last, position, transaction_pct,transaction_fixed)
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
