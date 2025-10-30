import numpy as np
import pandas as pd

def apply_min_hold(signals: pd.DataFrame, min_holding_period: int) -> pd.DataFrame:
    """
    Super-fast, rolling-based approximation for minimum holding period.
    Works only if signals are simple (1=entry, 0=exit).
    """
    out = signals.copy()
    s = out[col].copy()
    for col in out.columns: 
        # Identify entries (either +1 or -1)
        entry_points = s.isin([1, -1]).astype(int)

        # Track holding window with a counter
        hold_counter = np.zeros(len(s), dtype=int)

        last_entry_idx = -np.inf  # far in the past
        for i in range(len(s)):
            if s.iloc[i] in [1, -1]:
                last_entry_idx = i  # start new holding window
            if i - last_entry_idx < min_holding_period:
                hold_counter[i] = 1

        # Build mask
        hold_mask = hold_counter.astype(bool)

        # Mask *everything* inside hold window except the entry itself
        mask = hold_mask & (~entry_points.astype(bool))
        s[mask] = np.nan

        out[col] = s

    return out


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
