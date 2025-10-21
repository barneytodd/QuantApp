from .advanced_params import check_holding_period
from .pricing import calc_effective_price, commission
from app.strategies.signal_registry import generators

# --- 1. Check trading signal ---
def check_signal(position, date_idx, date, entry_date, data, params, strategy, lookback):
    """
    Determine trading signal for a given position and date.

    Args:
        position (int): 0 = no position, >0 = long, <0 = short
        date_idx (int): index of the current date in the dataset
        date (date): current date
        entry_date (dict): {"idx": idx, "date": date} when position was opened
        data (list/dict or DataFrame): price data
        params (dict): strategy parameters
        strategy (str): strategy name
        lookback (int): bars to skip at start

    Returns:
        str: trading signal ("buy", "sell", "hold", etc.)
    """
    if strategy == "pairs_trading" and (data.empty or data is None):
        return "hold"
    elif not data or len(data) == 0:
        return "hold"

    if date_idx < lookback:
        return "hold"

    # enforce minimum holding period
    if not check_holding_period(params.get("minHoldingPeriod", 0), position, entry_date, date_idx, date):
        return "hold"

    dates = data["date"].tolist() if strategy == "pairs_trading" else [row["date"] for row in data]
    try:
        i = dates.index(date)
    except ValueError:
        return "hold"

    signal = generators[strategy](data, i, params)

    # prevent invalid signal transitions
    if position <= 0 and signal in ["sell"]:
        return "hold"
    if position != 0 and signal in ["buy", "long", "short"]:
        return "hold"
    if position == 0 and signal == "exit":
        return "hold"

    return signal


# --- 2. Open a position ---
def open_position(signal, prices, capital, slippage_pct, transaction_pct, transaction_fixed):
    """
    Open positions based on signal.

    Args:
        signal (str): "buy", "short", etc.
        prices (list[float]): current prices for each stock
        capital (float): capital allocated to this strategy
        slippage_pct (float): fractional slippage
        transaction_pct (float): % transaction cost
        transaction_fixed (float): fixed transaction cost

    Returns:
        tuple: (positions list, updated capital, entry prices list)
    """
    actions = []
    if signal == "buy":
        actions.append("buy")
    elif signal == "short":
        actions.extend(["sell", "buy"])
    else:
        actions.extend(["buy", "sell"])

    new_positions = []
    entry_prices = []
    cap = capital

    for i, price in enumerate(prices):
        action = actions[i]
        effective_price = calc_effective_price(price, slippage_pct, action)

        if action == "buy":
            if signal == "buy":
                position = (cap - commission("buy", cap, effective_price, 0, transaction_pct, transaction_fixed)) / effective_price
            else:  # hedge/short setup
                position = cap / effective_price
        else:  # sell
            position = -1 * cap / effective_price

        new_positions.append(position)
        cap -= position * effective_price + commission(action, cap, effective_price, abs(position), transaction_pct, transaction_fixed)
        entry_prices.append(price)

    return new_positions, cap, entry_prices


# --- 3. Close a position ---
def close_position(symbols, prices, capital, entry_prices, positions, date, entry_date, slippage_pct, transaction_pct, transaction_fixed):
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

    for i, symbol in enumerate(symbols):
        position = positions[i]
        if position == 0:
            continue

        price = prices[i]
        entry_price = entry_prices[i]
        direction = "Long" if position > 0 else "Short"
        action = "sell" if position > 0 else "buy"
        entry_action = "buy" if position > 0 else "sell"

        effective_exit = calc_effective_price(price, slippage_pct, action)
        effective_entry = calc_effective_price(entry_price, slippage_pct, entry_action)

        pnl = position * (effective_exit - effective_entry)
        return_pct = (effective_exit - effective_entry) / effective_entry * 100 if direction == "Long" else (effective_entry - effective_exit) / effective_entry * 100

        trades.append({
            "symbol": symbol,
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

    return new_capital, trades
