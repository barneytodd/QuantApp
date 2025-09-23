from app.strategies.signal_generators import pairs_signal_generator
from collections import defaultdict
from app.utils.backtest_helpers import compute_metrics, compute_trade_stats, commission, calc_effective_price


def run_pairs_backtest(prices_df, params, stock1, stock2, initial_capital=10000):
    """
    Run a backtest for a pairs trading strategy on stock1 and stock2.
    
    prices_df: pd.DataFrame with columns [stock1, stock2, "date"]
    params: dict with keys ["lookback", "entryZ", "exitZ"]
    """
    series1 = prices_df[stock1].values
    series2 = prices_df[stock2].values
    dates = prices_df["date"].tolist()

    slippage_pct = params["slippage"] / 100
    commission_pct = params["transactionCostPct"] / 100
    commission_fixed = params["fixedTransactionCost"]
    
    capital = initial_capital
    position = 0   # +1 = long stock1/short stock2, -1 = short stock1/long stock2
    equity_curve = []
    trades = []
    entry_price1, entry_price2 = None, None
    entry_date = None
    units1, units2 = 0, 0  # Number of shares per leg

    def open_position(direction, price1, price2, date):
        nonlocal capital, units1, units2, entry_price1, entry_price2, entry_date, position

        if position != 0:
            return

        position = 1 if direction == "long" else -1
        action = ["buy", "sell"] if position == 1 else ["sell", "buy"]

        entry_price1, entry_price2, entry_date = price1, price2, date
        capital_per_leg = capital / 2

        units1 = capital_per_leg / calc_effective_price(price1, slippage_pct, action[0])
        units2 = capital_per_leg / calc_effective_price(price2, slippage_pct, action[1])
        
        capital -= commission(action[0], capital_per_leg, price1, units1, commission_pct, commission_fixed)
        capital -= commission(action[1], capital_per_leg, price2, units2, commission_pct, commission_fixed)
        

    def close_position(price1, price2, date, is_final=False):
        nonlocal capital, position, units1, units2, entry_price1, entry_price2, entry_date

        if position == 0:
            return
        
        action = ["sell", "buy"] if position == 1 else ["buy", "sell"]

        if position == 1:  
            pnl1 = (calc_effective_price(price1, slippage_pct, "sell") - calc_effective_price(entry_price1, slippage_pct, "buy")) * units1
            pnl2 = (calc_effective_price(entry_price2, slippage_pct, "sell") - calc_effective_price(price2, slippage_pct, "buy")) * units2
        else:  
            pnl1 = (calc_effective_price(entry_price1, slippage_pct, "sell") - calc_effective_price(price1, slippage_pct, "buy")) * units1
            pnl2 = (calc_effective_price(price2, slippage_pct, "sell") - calc_effective_price(entry_price2, slippage_pct, "buy")) * units2

        exit_commission = (
            commission(action[0], 0, price1, units1, commission_pct, commission_fixed) +
            commission(action[1], 0, price2, units2, commission_pct, commission_fixed)
        )

        capital += pnl1 + pnl2 - exit_commission

        trades.extend([
            {
                "stock": stock1,
                "direction": "long" if position == 1 else "short",
                "entryDate": entry_date,
                "exitDate": date,
                "entryPrice": entry_price1,
                "exitPrice": price1,
                "units": units1,
                "pnl": pnl1,
                "returnPct": pnl1 / (entry_price1 * units1) * 100,
            },
            {
                "stock": stock2,
                "direction": "short" if position == 1 else "long",
                "entryDate": entry_date,
                "exitDate": date,
                "entryPrice": entry_price2,
                "exitPrice": price2,
                "units": units2,
                "pnl": pnl2,
                "returnPct": pnl2 / (entry_price2 * units2) * 100,
            },
        ])

    for i in range(len(series1)):
        price1, price2 = series1[i], series2[i]
        date = dates[i]

        signal = pairs_signal_generator(
            [{"date": dates[j], stock1: series1[j], stock2: series2[j]} for j in range(len(series1))],
            i,
            {**params, "stock1": stock1, "stock2": stock2}
        )

        # ENTER POSITION
        if signal in ["long", "short"]:
            open_position(signal, price1, price2, date)

        # EXIT POSITION
        elif signal == "exit": 
            close_position(price1, price2, date)

            # Reset position
            position = 0
            entry_price1, entry_price2 = None, None
            units1, units2 = 0, 0
            entry_date = None

        # Update equity curve
        if position != 0:
            if position == 1:
                unrealized = calc_effective_price(price1, slippage_pct, "sell") * units1 - calc_effective_price(price2, slippage_pct, "buy") * units2
            else:
                unrealized = calc_effective_price(price2, slippage_pct, "sell") * units2 - calc_effective_price(price1, slippage_pct, "buy") * units1
            equity_curve.append({"date": date, "value": capital + unrealized})
        else:
            equity_curve.append({"date": date, "value": capital})

    # FINAL LIQUIDATION
    if position != 0:
        price1, price2, date = series1[-1], series2[-1], dates[-1]

        close_position(price1, price2, date, is_final=True)

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
