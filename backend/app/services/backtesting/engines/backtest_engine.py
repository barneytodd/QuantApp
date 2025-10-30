import pandas as pd

from ..helpers.backtest import (
    generate_signals, open_position, close_position,
    compute_metrics, compute_trade_stats,
    rebalance, prepare_price_matrix
)
from ..helpers.pairs import align_series

def run_backtest(data, symbols, params, lookback=0, progress_callback=None):
    """
    Run a backtest for single-stock and pairs trading strategies.

    Args:
        data (dict): 
            Mapping of symbol -> list of OHLC data dictionaries
            Example: { "AAPL": [ {"date":..., "close":...}, ... ] }
        symbols (dict): 
            Mapping of symbol_strategy_key -> symbol/strategy info
            Example: { "sym1_strat": { "symbols": ["AAPL"], "strategy": "momentum", "weight": 1 } }
        params (dict): 
            Backtest parameters (initialCapital, slippage, transaction costs, etc.)
        lookback (int): 
            Number of initial bars to skip (warm-up)
        progress_callback (callable): 
            Optional callback to report progress per date index

    Returns:
        list of dicts: equity curves, trades, and metrics per strategy_key
    """
    # --- 0. Extract common parameters ---
    slippage_pct = params["slippage"] / 100
    transaction_pct = params["transactionCostPct"] / 100
    transaction_fixed = params["fixedTransactionCost"]
    initial_capital = params["initialCapital"]

    # --- 1. Convert raw OHLC lists to DataFrames for fast lookup ---
    price_matrix = prepare_price_matrix(data)

    # --- 2. Generate signals ---
    signal_matrix = generate_signals(price_matrix, symbols, params)
    signal_matrix = signal_matrix.ffill()
    signal_matrix = signal_matrix.fillna(0)

    trade_indicator = signal_matrix.diff().fillna(signal_matrix.iloc[0])
    trade_indicator = trade_indicator.astype(int)
    position_indicator = trade_indicator.cumsum()

    entry_date_matrix = pd.DataFrame(pd.NaT, index=trade_indicator.index, columns=trade_indicator.columns)
    date_series = pd.Series(trade_indicator.index, index=trade_indicator.index)

    for col in trade_indicator.columns:
        entry_date_matrix.loc[trade_indicator[col] != 0, col] = date_series[trade_indicator[col] != 0]

    entry_date_matrix = entry_date_matrix.ffill()
    entry_date_matrix = entry_date_matrix.shift(1)

    all_trades = {}
    equity_matrix = pd.DataFrame(0.0, index=trade_indicator.index, columns=trade_indicator.columns)
    
    # --- 3. Execute trades ---
    idx = 0
    for symbol_key, info in symbols.items():
        syms = info["symbols"]
        strat = info["strategy"]
        capital = initial_capital * info["weight"]
        positions = [0] * len(syms)
        for sym in syms:
            all_trades[symbol_key] = []
        for date in trade_indicator.index:
            trade = trade_indicator.at[date, symbol_key]
            pos = position_indicator.at[date, symbol_key]
            if trade == 0:
                pass
            elif pos == 0:
                capital, positions, trades = close_position(
                    syms, price_matrix[syms], capital, positions, 
                    entry_date_matrix.at[date, symbol_key], date,
                    slippage_pct, transaction_pct, transaction_fixed
                )
                all_trades[symbol_key].extend([trade for trade in trades if trade["symbol"] in syms])
            else:
                positions, capital = open_position(
                    strat, trade, price_matrix[syms],
                    date, capital, positions,
                    syms, slippage_pct, transaction_pct, transaction_fixed
                )
            equity_matrix.loc[date, symbol_key] = capital + sum(
                position * price_matrix.at[date, sym] for position, sym in zip(positions, syms)
            )
        
        idx += 1
        print(f"Progress: {idx}/{len(symbols.keys())}", end='\r')
        if progress_callback:
            try:
                progress_callback(idx, len(symbols.keys()))
            except Exception as e:
                print(e)
                pass


    equity_matrix["overall"] = equity_matrix.sum(axis=1)

    # --- 4. Build results ---
    results = []
    for strategy_key in equity_matrix.columns:
        curve = [
            {"date": date.strftime("%Y-%m-%d"), "value": float(value)}
            for date, value in equity_matrix[strategy_key].items()
        ]
        initial = initial_capital * symbols[strategy_key]["weight"] if strategy_key != "overall" else sum([initial_capital * symbols[strategy_key]["weight"] for strategy_key in symbols])
        strategy_trades = all_trades[strategy_key] if strategy_key != "overall" else [trade for trade_list in all_trades.values() for trade in trade_list]
        results.append({
            "symbol": strategy_key if strategy_key != "overall" else "overall",
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
