from ..helpers.backtest.positions import check_signal, open_position, close_position
from ..helpers.backtest.metrics import compute_metrics, compute_trade_stats
from ..helpers.pairs.align_series import align_series
from ..helpers.backtest.advanced_params import rebalance

def run_backtest(data, symbols, params, lookback=0):
    """
    data: dict {symbol: [{"date":..., "close":...}, ...]} - stores data separately for each symbol
    symbols: dict { symbol: {"strategy": strat, "weight": wgt} } - stores pairs as single symbols
    params: dict of strategy parameters
    lookback: int - lookback period to initiate indicators before first trading day
    """
    slippage_pct = params["slippage"] / 100
    transaction_pct = params["transactionCostPct"] / 100
    transaction_fixed = params["fixedTransactionCost"] 
    initial_capital = params["initialCapital"]

    capital = {symbol:initial_capital * strat_info["weight"] for symbol,strat_info in symbols.items()}
    positions = {symbol:0 for symbol in data.keys()}
    equity_curves = {**{symbol: [] for symbol in symbols.keys()}, "overall": []}
    trades = {symbol:[] for symbol in symbols.keys()}
    entry_prices = {symbol:None for symbol in data.keys()}
    entry_dates = {symbol:{"idx":None, "date":None} for symbol in symbols.keys()}
    last_prices = {symbol:None for symbol in data.keys()}
    current_prices = {symbol:None for symbol in data.keys()}

    all_dates = sorted({row["date"] for d in data.values() for row in d})

    for idx, date in enumerate(all_dates):
        
        # --- 1. Generate signals ---
        signals = {}
        for symbol, strat_info in symbols.items():
            strategy = strat_info["strategy"]
            if strategy == "pairs_trading":
                stocks = symbol.split("-")
                prices_dict = {stock: data[stock] for stock in stocks}
                symbol_data = align_series(prices_dict, stocks[0], stocks[1])
            else:
                stocks = [symbol]
                symbol_data = data[symbol]

            data_check = True
            for stock in stocks:
                price = next((d["close"] for d in data[stock] if d["date"] == date), None)
                current_prices[stock] = price
                if price is None:
                    data_check = False
                else:
                    last_prices[stock] = price

            if data_check:
                signal = check_signal(positions[stocks[0]], idx, date, entry_dates[symbol], symbol_data, params, strategy, lookback)
                signals[symbol] = signal
            else:
                signals[symbol] = "hold"


        # --- 2. Apply exits ---
        for symbol, signal in signals.items():
            if signal in ["sell", "exit"]:
                if symbols[symbol]["strategy"] == "pairs_trading":
                    stocks = symbol.split("-")
                else:
                    stocks = [symbol]
                prices = [current_prices[s] for s in stocks]
                entry_ps = [entry_prices[s] for s in stocks]
                pos = [positions[s] for s in stocks]
                
                capital[symbol], new_trades = close_position(
                    stocks,
                    prices,
                    capital[symbol],
                    entry_ps,
                    pos, 
                    date, 
                    entry_dates[symbol]["date"],
                    slippage_pct,
                    transaction_pct,
                    transaction_fixed
                )
                trades[symbol].extend(new_trades)
                for s in stocks:
                    positions[s] = 0
                    entry_prices[s] = None
                entry_dates[symbol]["idx"] = entry_dates[symbol]["date"] = None


        # --- 3. Apply entries ---
        for symbol, signal in signals.items():
            if signal in ["buy", "short", "long"]:
                
                if symbols[symbol]["strategy"] == "pairs_trading":
                    stocks = symbol.split("-")
                else:
                    stocks = [symbol]

                prices = [current_prices[s] for s in stocks]
                cap = capital[symbol]

                new_positions, capital[symbol], new_entry_prices = open_position(
                            signal, prices, cap, slippage_pct, transaction_pct, transaction_fixed
                )

                for i, stock in enumerate(stocks):
                    positions[stock] = new_positions[i]
                    entry_prices[stock] = new_entry_prices[i]
                
                entry_dates[symbol]["idx"], entry_dates[symbol]["date"] = idx, date

        
        # --- 4. Apply rebalancing ---
        #freq = params["rebalanceFrequency"]
        #lookback = params["volLookback"]
        #if freq not in [0, "onSignal"] and idx%int(freq) == 0 and lookback <= idx:
        #    pass
            #positions = rebalance(equity_curves, positions, current_prices, float(params["volTarget"])/100, lookback)

        # --- 5. Mark portfolio value ---
        if idx >= lookback:
            for symbol, strat_info in symbols.items():
                if strat_info["strategy"] == "pairs_trading":
                    stocks = symbol.split("-")
                else:
                    stocks = [symbol]
                value = capital[symbol]
                for stock in stocks:
                    price = current_prices[stock]
                    if price is not None:
                        value += positions[stock] * price
                    else:
                        value = None
                        break
                if value is not None:
                    equity_curves[symbol].append({"date": date, "value": value})
                    

            portfolio_value = close_position(
                [stock for stock in data.keys()],
                [last_prices[s] for s in data.keys()],
                sum(capital.values()),
                [p for p in entry_prices.values()],
                [pos for pos in positions.values()], 
                date, 
                None,
                0,
                0,
                0
            )[0]
            equity_curves["overall"].append({"date": date, "value": portfolio_value})

    results = []
    for symbol, equity_curve in equity_curves.items():
        initialCapital = initial_capital / len(symbols) if symbol != "overall" else initial_capital
        symbol_trades = trades[symbol] if symbol != "overall" else [trade for trade_list in trades.values() for trade in trade_list]
        results.append({
            "symbol": symbol,
            "initialCapital": initialCapital,
            "finalCapital": equity_curve[-1]["value"],
            "returnPct": (equity_curve[-1]["value"] / initialCapital - 1) * 100,
            "metrics": compute_metrics(equity_curve),
            "equityCurve": equity_curve,
            "trades": symbol_trades,
            "tradeStats": compute_trade_stats(symbol_trades)
        })

    return results
