import pandas as pd

from .advanced_params import apply_min_hold
from .pricing import calc_effective_price, commission
from app.strategies.signal_registry import generators

# --- 1. Check trading signal ---
def generate_signals(price_matrix: pd.DataFrame, symbols: dict, params=None):
    """
    Produce a signal matrix for all symbol-strategy pairs

    Args:
        price_matrix (pd.DataFrame): prices with dates as index and symbols as columns
        symbols (dict): symbol_strategy_key: symbol and strategy info, for which to get signals
        params (dict, optional): parameters for the strategies

    Returns:
        int or pd.Series: 1 = long/buy, 0 = exit, np.nan = hold, -1 = short (pairs trading only)
    """
    if price_matrix is None or price_matrix.empty:
        # No data available, cannot generate signal
        if symbols and len(symbols.keys()) == 1:
            return pd.Series([pd.NA], index=list(symbols.keys()))
        elif symbols:
            return pd.Series([pd.NA] * len(symbols.keys()), index=list(symbols.keys()))
        else:
            return pd.NA

    if params is None:
        params = {}

    all_signals = []
    strat_dict = {}
    # Generate signals matrix or series
    for key, info in symbols.items():
        strategy = info["strategy"]
        symbol_list = info["symbols"]
        strat_dict.setdefault(strategy, {})[key] = symbol_list

    for strat, items in strat_dict.items():
        generator = generators.get(strat)
        if generator is None:
            raise ValueError(f"Strategy '{strat}' is not registered.")
        sub_prices = price_matrix[[sym for symbols in items.values() for sym in symbols]]
        signals_db = pd.DataFrame(index=sub_prices.index)
        if strat == "pairs_trading":
            for key, pair in items.items():
                signals = generator(sub_prices, pair[0], pair[1], params)
                signals.name = key
                signals_db[key] = signals
                
        else:
            # Generate signals
            signals = generator(sub_prices, params)
            if isinstance(signals, pd.Series):
                signals = signals.to_frame(name=f"{key}_{strat}")
            signals.columns = [f"{col}_{strat}" for col in signals.columns]
            signals_db = signals
            
        min_hold = params.get("minHoldingPeriod", 0)
        if min_hold > 0:
            signals_db = apply_min_hold(signals_db, min_hold)

        all_signals.append(signals_db)

    # Combine into one DataFrame
    signal_matrix = pd.concat(all_signals, axis=1)
    return signal_matrix


# --- 2. Open a position ---
def open_position(
    strategy: str,
    signal: int,
    prices: pd.DataFrame,
    date: pd.Timestamp,
    capital: float,
    positions: list[float],
    symbols: list[str],
    slippage_pct: float,
    transaction_pct: float,
    transaction_fixed: float
):
    """
    Open positions based on signal.

    Args:
        strategy: strategy name ("momentum", "pairs_trading", etc.)
        signal: +1 for long, -1 for short, 0 for flat
        prices: full price DataFrame (dates x symbols)
        capital: current available capital
        positions: current list of position quantities
        symbols: list of involved symbols (1 or 2)
        slippage_pct, transaction_pct, transaction_fixed: cost parameters
    """
    actions = []
    if signal == 1 and strategy != "pairs_trading":
        actions.append("buy")
    elif signal == -1:
        actions.extend(["sell", "buy"])
    else:
        actions.extend(["buy", "sell"])

    new_positions = []
    cap = capital

    for sym, action in zip(symbols, actions):
        price = prices.at[date, sym]
        effective_price = calc_effective_price(price, slippage_pct, action)

        if action == "buy":
            if strategy != "pairs_trading":
                position = (capital - commission("buy", capital, effective_price, 0, transaction_pct, transaction_fixed)) / effective_price
            else:  # hedge/short setup
                position = capital / effective_price
        else:  # sell
            position = -1 * capital / effective_price

        new_positions.append(position)
        cap -= position * effective_price + commission(action, cap, effective_price, abs(position), transaction_pct, transaction_fixed)

    return new_positions, cap


# --- 3. Close a position ---
def close_position(
    symbols: list[str],
    prices: pd.DataFrame,
    capital: float,
    positions: list[float],
    entry_date: pd.Timestamp,
    date: pd.Timestamp,
    slippage_pct: float,
    transaction_pct: float,
    transaction_fixed: float
):
    """
    Close existing positions and compute trade PnL.

    Args:
        symbols (list[str]): stock symbols
        prices (list[float]): current prices
        capital (float): current capital
        entry_prices (list[float]): entry prices for positions
        positions (list[float]): current positions
        date (date): exit date
        entry_date (date): entry date
        slippage_pct, transaction_pct, transaction_fixed: trading costs

    Returns:
        tuple: (updated capital, list of trades)
    """
    new_capital = capital
    trades = []

    for sym, position in zip(symbols, positions):
        if position == 0:
            continue

        price = prices.at[date, sym]
        entry_price = prices.at[entry_date, sym]
        direction = "Long" if position > 0 else "Short"
        action = "sell" if position > 0 else "buy"
        entry_action = "buy" if position > 0 else "sell"

        effective_exit = calc_effective_price(price, slippage_pct, action)
        effective_entry = calc_effective_price(entry_price, slippage_pct, entry_action)

        pnl = position * (effective_exit - effective_entry)
        return_pct = (effective_exit - effective_entry) / effective_entry * 100 if direction == "Long" else (effective_entry - effective_exit) / effective_entry * 100

        trades.append({
            "symbol": sym,
            "direction": direction,
            "entryDate": entry_date,
            "exitDate": date,
            "entryPrice": entry_price,
            "exitPrice": price,
            "pnl": pnl,
            "returnPct": return_pct
        })

        new_capital += position * effective_exit
        new_capital -= commission(action, capital if action=="sell" else -position*effective_exit, effective_exit, position, transaction_pct, transaction_fixed)

    return new_capital, [0] * len(symbols), trades
