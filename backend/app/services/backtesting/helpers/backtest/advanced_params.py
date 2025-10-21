import numpy as np

def check_holding_period(min_holding_period: int, position: int, entry_date: dict, date_idx: int, date) -> bool:
    """
    Check if a position has been held long enough according to a minimum holding period.

    Args:
        min_holding_period (int): Minimum number of bars/days to hold a position
        position (int): Current position size (0 = no position)
        entry_date (dict): {"idx": int, "date": datetime} of when position was opened
        date_idx (int): Current index of the date in backtest
        date (datetime): Current date (for reference)
    
    Returns:
        bool: True if position can be held or acted upon, False if still in minimum holding period
    """
    # No restriction if no min period or no open position
    if min_holding_period == 0 or position == 0:
        return True

    # Calculate how many bars the position has been open
    diff = date_idx - entry_date["idx"]
    return diff >= min_holding_period


def rebalance(equity_curves: dict, positions: dict, prices: dict, target_vol: float, lookback: int) -> dict:
    """
    Rebalance portfolio positions based on a target volatility.

    Args:
        equity_curves (dict): {strategy_key: [{"date": ..., "value": ...}, ...]}
        positions (dict): {symbol: current_position_size}
        prices (dict): {symbol: current_price}
        target_vol (float): Annualized target volatility (e.g., 0.1 for 10%)
        lookback (int): Number of periods to compute covariance matrix
    
    Returns:
        dict: Adjusted positions scaled by volatility target
    """
    # 1. Compute returns matrix for all strategies (except "overall")
    returns = np.array([
        np.diff(np.log([e["value"] for e in equity_curves[s]])) 
        for s in equity_curves if s != "overall"
    ]).T  # shape = (n_obs, n_strategies)

    # 2. Use only last `lookback` observations
    window = returns[-lookback:, :] if lookback > 0 else returns
    cov = np.cov(window.T, bias=False)  # covariance of strategies
    cov_annual = cov * 252  # annualize (assuming 252 trading days)

    # 3. Compute current total portfolio exposure
    total_exposure = sum(positions[s] * prices[s] for s in positions)
    if total_exposure == 0:
        return positions

    # 4. Current weights
    weights = np.array([positions[s] * prices[s] / total_exposure for s in positions])

    # 5. Compute portfolio volatility
    port_var = np.dot(weights, np.dot(cov_annual, weights))
    port_vol = np.sqrt(port_var)

    # Avoid division by zero
    if port_vol == 0:
        return positions

    # 6. Scale positions by volatility target
    scaling_factor = target_vol / port_vol
    return {s: scaling_factor * p for s, p in positions.items()}
