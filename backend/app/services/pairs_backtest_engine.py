from app.services.buy_sell_signals import pairs_signal_generator
from collections import defaultdict
from .backtest_engine import compute_metrics, compute_trade_stats, commission

def run_pairs_backtest(prices_df, params, stock1, stock2, initial_capital=10000, slippage_pct=0.0005, commission_pct=0.001, commission_fixed=0.0):
    """
    Run a backtest for a pairs trading strategy on stock1 and stock2.
    
    prices_df: pd.DataFrame with columns [stock1, stock2, "date"]
    params: dict with keys ["lookback", "entryZ", "exitZ"]
    """
    series1 = prices_df[stock1].values
    series2 = prices_df[stock2].values
    dates = prices_df["date"].tolist()
    
    capital = initial_capital
    position = 0   # +1 = long stock1/short stock2, -1 = short stock1/long stock2
    equity_curve = []
    trades = []
    entry_price1, entry_price2 = None, None
    entry_date = None
    units1, units2 = 0, 0  # Number of shares per leg

    for i in range(len(series1)):
        price1, price2 = series1[i], series2[i]
        date = dates[i]

        signal = pairs_signal_generator(
            [{"date": dates[j], stock1: series1[j], stock2: series2[j]} for j in range(len(series1))],
            i,
            {**params, "stock1": stock1, "stock2": stock2}
        )

        # ENTER POSITION
        if signal in ["long", "short"] and position == 0:
            position = 1 if signal == "long" else -1
            entry_price1, entry_price2 = price1, price2
            entry_date = date

            # Allocate half capital to each leg
            capital_per_leg = capital / 2
            units1 = capital_per_leg / (price1 * (1 + slippage_pct))
            units2 = capital_per_leg / (price2 * (1 + slippage_pct))

            # Deduct entry commissions
            capital -= commission("buy", capital / 2, price1, units1, commission_pct, commission_fixed)
            capital -= commission("buy", capital / 2, price2, units2, commission_pct, commission_fixed)

        # EXIT POSITION
        elif signal == "exit" and position != 0:
            if position == 1:  # long stock1 / short stock2
                pnl1 = (price1 * (1 - slippage_pct) - entry_price1 * (1 + slippage_pct)) * units1
                pnl2 = (entry_price2 * (1 + slippage_pct) - price2 * (1 - slippage_pct)) * units2
            else:  # short stock1 / long stock2
                pnl1 = (entry_price1 * (1 + slippage_pct) - price1 * (1 - slippage_pct)) * units1
                pnl2 = (price2 * (1 - slippage_pct) - entry_price2 * (1 + slippage_pct)) * units2

            exit_commission = commission("sell", 0, price1, units1, commission_pct, commission_fixed) + \
                              commission("sell", 0, price2, units2, commission_pct, commission_fixed)

            capital += pnl1 + pnl2 - exit_commission

            # Record trades per leg
            trades.append({
                "stock": stock1,
                "direction": "long" if position == 1 else "short",
                "entryDate": entry_date,
                "exitDate": date,
                "entryPrice": entry_price1,
                "exitPrice": price1,
                "units": units1,
                "pnl": pnl1 - commission("sell", 0, price1, units1, commission_pct, commission_fixed),
                "returnPct": (pnl1 - commission("sell", 0, price1, units1, commission_pct, commission_fixed)) / (entry_price1 * units1) * 100
            })
            trades.append({
                "stock": stock2,
                "direction": "short" if position == 1 else "long",
                "entryDate": entry_date,
                "exitDate": date,
                "entryPrice": entry_price2,
                "exitPrice": price2,
                "units": units2,
                "pnl": pnl2 - commission("sell", 0, price2, units2, commission_pct, commission_fixed),
                "returnPct": (pnl2 - commission("sell", 0, price2, units2, commission_pct, commission_fixed)) / (entry_price2 * units2) * 100
            })

            # Reset position
            position = 0
            entry_price1, entry_price2 = None, None
            units1, units2 = 0, 0
            entry_date = None

        # Update equity curve
        if position != 0:
            if position == 1:
                unrealized = (price1 - entry_price1) * units1 + (entry_price2 - price2) * units2
            else:
                unrealized = (entry_price1 - price1) * units1 + (price2 - entry_price2) * units2
            equity_curve.append({"date": date, "value": capital + unrealized})
        else:
            equity_curve.append({"date": date, "value": capital})

    # FINAL LIQUIDATION
    if position != 0:
        price1, price2, date = series1[-1], series2[-1], dates[-1]
        if position == 1:
            pnl1 = (price1 * (1 - slippage_pct) - entry_price1 * (1 + slippage_pct)) * units1
            pnl2 = (entry_price2 * (1 + slippage_pct) - price2 * (1 - slippage_pct)) * units2
        else:
            pnl1 = (entry_price1 * (1 + slippage_pct) - price1 * (1 - slippage_pct)) * units1
            pnl2 = (price2 * (1 - slippage_pct) - entry_price2 * (1 + slippage_pct)) * units2

        exit_commission = commission("sell", 0, price1, units1, commission_pct, commission_fixed) + \
                          commission("sell", 0, price2, units2, commission_pct, commission_fixed)

        capital += pnl1 + pnl2 - exit_commission

        # Record final trades
        trades.append({
            "stock": stock1,
            "direction": "long" if position == 1 else "short",
            "entryDate": entry_date,
            "exitDate": date,
            "entryPrice": entry_price1,
            "exitPrice": price1,
            "units": units1,
            "pnl": pnl1 - commission("sell", 0, price1, units1, commission_pct, commission_fixed),
            "returnPct": (pnl1 - commission("sell", 0, price1, units1, commission_pct, commission_fixed)) / (entry_price1 * units1) * 100
        })
        trades.append({
            "stock": stock2,
            "direction": "short" if position == 1 else "long",
            "entryDate": entry_date,
            "exitDate": date,
            "entryPrice": entry_price2,
            "exitPrice": price2,
            "units": units2,
            "pnl": pnl2 - commission("sell", 0, price2, units2, commission_pct, commission_fixed),
            "returnPct": (pnl2 - commission("sell", 0, price2, units2, commission_pct, commission_fixed)) / (entry_price2 * units2) * 100
        })

    return {
        "symbol": f"{stock1}-{stock2}",
        "initialCapital": initial_capital,
        "finalCapital": capital,
        "returnPct": (capital / initial_capital - 1) * 100,
        "equityCurve": equity_curve,
        "trades": trades,
        "metrics": compute_metrics(equity_curve),
        "tradeStats": compute_trade_stats(trades)
    }




def combine_pairs_results(results):
    """
    Combine multiple pairs backtests into a single overall result.
    
    Args:
        results: list of dicts returned by run_pairs_backtest()
    
    Returns:
        dict with combined equity curve, trades, initial/final capital, etc.
    """
    date_map = defaultdict(float)
    combined_trades = []

    # Gather all unique dates
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
            date_map[date] += last_value

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
