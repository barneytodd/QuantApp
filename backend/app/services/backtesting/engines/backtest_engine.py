from ..helpers.backtest.positions import check_signal, open_position, close_position
from ..helpers.backtest.metrics import compute_metrics, compute_trade_stats
from ..helpers.pairs.align_series import align_series
from ..helpers.backtest.advanced_params import rebalance

def run_backtest(data, symbols, params, lookback=0):
    """
    Run a backtest for single-stock and pairs strategies.

    Args:
        data (dict): { symbol: [ { "date": ..., "close": ... }, ... ] }
        symbols (dict): { key: { "symbol": "AAPL", "strategy": "momentum", "weight": 1 } }
        params (dict): global and strategy-specific parameters
        lookback (int): initial bars to skip

    Returns:
        list of dicts with equity curves, trades, and metrics per symbol-strategy key
    """

    slippage_pct = params["slippage"] / 100
    transaction_pct = params["transactionCostPct"] / 100
    transaction_fixed = params["fixedTransactionCost"] 
    initial_capital = params["initialCapital"]

    # --- initialize structures ---
    # capital and tracking per strategy_key
    capital = {strategy_key: info["weight"] * initial_capital for strategy_key, info in symbols.items()}
    equity_curves = {strategy_key: [] for strategy_key in symbols.keys()}
    equity_curves["overall"] = []
    trades = {strategy_key: [] for strategy_key in symbols.keys()}
    entry_dates = {strategy_key: {"idx": None, "date": None} for strategy_key in symbols.keys()}

    # positions and entry_prices per stock per strategy
    positions = {stock: {k:0 for k,s in symbols.items() if stock in s["symbol"].split("-")} for stock in data.keys()}
    entry_prices = {stock: {k:None for k,s in symbols.items() if stock in s["symbol"].split("-")} for stock in data.keys()}

    # track last/current prices per stock
    last_prices = {stock: None for stock in data.keys()}
    current_prices = {stock: None for stock in data.keys()}

    all_dates = sorted({row["date"] for d in data.values() for row in d})

    for idx, date in enumerate(all_dates):
        signals = {}

        # --- 1. Generate signals per strategy ---
        for strategy_key, info in symbols.items():
            strategy = info["strategy"]
            if strategy == "pairs_trading":
                stocks = info["symbol"].split("-")
                prices_dict = {stock: data[stock] for stock in stocks}
                strategy_data = align_series(prices_dict, stocks[0], stocks[1])
            else:
                stocks = [info["symbol"]]
                strategy_data = data[stocks[0]]

            # update current prices and check for missing data
            data_ok = True
            for stock in stocks:
                price = next((d["close"] for d in data[stock] if d["date"] == date), None)
                current_prices[stock] = price
                if price is None:
                    data_ok = False
                else:
                    last_prices[stock] = price

            if data_ok:
                signal = check_signal(
                    positions[stocks[0]][strategy_key], idx, date,
                    entry_dates[strategy_key], strategy_data, params, strategy, lookback
                )
                signals[strategy_key] = signal
            else:
                signals[strategy_key] = "hold"


        # --- 2. Apply exits ---
        if signal in ["sell", "exit"]:
                info = symbols[strategy_key]
                stocks = info["symbol"].split("-") if info["strategy"] == "pairs_trading" else [info["symbol"]]

                pos_list = [positions[stock][strategy_key] for stock in stocks]
                entry_list = [entry_prices[stock][strategy_key] for stock in stocks]
                price_list = [current_prices[stock] for stock in stocks]

                capital[strategy_key], new_trades = close_position(
                    stocks,
                    price_list,
                    capital[strategy_key],
                    entry_list,
                    pos_list,
                    date,
                    entry_dates[strategy_key]["date"],
                    slippage_pct,
                    transaction_pct,
                    transaction_fixed
                )

                trades[strategy_key].extend(new_trades)
                for stock in stocks:
                    positions[stock][strategy_key] = 0
                    entry_prices[stock][strategy_key] = None
                entry_dates[strategy_key]["idx"] = entry_dates[strategy_key]["date"] = None


        # --- 3. Apply entries ---
        for strategy_key, signal in signals.items():
            if signal in ["buy", "short", "long"]:
                info = symbols[strategy_key]
                stocks = info["symbol"].split("-") if info["strategy"] == "pairs_trading" else [info["symbol"]]
                price_list = [current_prices[stock] for stock in stocks]
                cap = capital[strategy_key]

                new_pos, capital[strategy_key], new_entry_prices = open_position(
                    signal, price_list, cap, slippage_pct, transaction_pct, transaction_fixed
                )

                for i, stock in enumerate(stocks):
                    positions[stock][strategy_key] = new_pos[i]
                    entry_prices[stock][strategy_key] = new_entry_prices[i]

                entry_dates[strategy_key]["idx"], entry_dates[strategy_key]["date"] = idx, date

        
        # --- 4. Apply rebalancing ---
        #freq = params["rebalanceFrequency"]
        #lookback = params["volLookback"]
        #if freq not in [0, "onSignal"] and idx%int(freq) == 0 and lookback <= idx:
        #    pass
            #positions = rebalance(equity_curves, positions, current_prices, float(params["volTarget"])/100, lookback)

        # --- 5. Mark portfolio value ---
        if idx >= lookback:
            for strategy_key, info in symbols.items():
                stocks = info["symbol"].split("-") if info["strategy"] == "pairs_trading" else [info["symbol"]]
                value = capital[strategy_key]
                for stock in stocks:
                    price = current_prices[stock]
                    if price is not None:
                        value += positions[stock][strategy_key] * price
                    else:
                        value = None
                        break
                if value is not None:
                    equity_curves[strategy_key].append({"date": date, "value": value})
                    

            all_stocks = list(data.keys())
            overall_positions = [sum(positions[stock].values()) for stock in all_stocks]
            overall_entry_prices = [sum(filter(None, entry_prices[stock].values())) for stock in all_stocks]  # sum only non-None

            portfolio_value = close_position(
                all_stocks,
                [last_prices[s] for s in all_stocks],
                sum(capital.values()),
                overall_entry_prices,
                overall_positions,
                date,
                None,
                0,
                0,
                0
            )[0]
            equity_curves["overall"].append({"date": date, "value": portfolio_value})

    results = []
    for strategy_key, curve in equity_curves.items():
        initial = initial_capital * symbols[strategy_key]["weight"] if strategy_key != "overall" else initial_capital
        strategy_trades = trades[strategy_key] if strategy_key != "overall" else [trade for trade_list in trades.values() for trade in trade_list]
        results.append({
            "symbol": symbols[strategy_key]["symbol"] if strategy_key != "overall" else "overall",
            "strategy": symbols[strategy_key]["strategy"] if strategy_key != "overall" else "overall",
            "initialCapital": initial,
            "finalCapital": curve[-1]["value"] if curve else None,
            "returnPct": ((curve[-1]["value"]/initial - 1)*100) if curve else None,
            "equityCurve": curve,
            "trades": strategy_trades,
            "metrics": compute_metrics(curve),
            "tradeStats": compute_trade_stats(strategy_trades)
        })

    return results
