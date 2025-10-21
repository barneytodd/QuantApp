# --- 1. Commission calculation ---
def commission(
    signal: str = "buy",
    capital: float = 0,
    effective_price: float = 0,
    position: float = 0,
    commission_pct: float = 0.001,
    commission_fixed: float = 0.0
) -> float:
    """
    Calculate transaction costs for a trade.

    Args:
        signal (str): "buy" or "sell"
        capital (float): capital allocated for the trade (for buy)
        effective_price (float): price at which the trade occurs
        position (float): number of shares/contracts (for sell)
        commission_pct (float): percentage commission
        commission_fixed (float): fixed commission cost

    Returns:
        float: total commission cost
    """
    if signal.lower() == "buy":
        # Buy commission is typically proportional to capital spent
        # Divide by (1 + commission_pct) to adjust for including commission in capital allocation
        return (capital * commission_pct + commission_fixed) / (1 + commission_pct)
    else:
        # Sell commission is proportional to position value
        return abs(position) * effective_price * commission_pct + commission_fixed


# --- 2. Effective price calculation considering slippage ---
def calc_effective_price(
    price: float,
    slippage_pct: float = 0.001,
    signal: str = "buy"
) -> float:
    """
    Compute the effective trade price including slippage.

    Args:
        price (float): raw market price
        slippage_pct (float): fractional slippage per trade
        signal (str): "buy" or "sell"

    Returns:
        float: adjusted price including slippage
    """
    if signal.lower() == "buy":
        return price * (1 + slippage_pct)
    else:  # sell
        return price * (1 - slippage_pct)
