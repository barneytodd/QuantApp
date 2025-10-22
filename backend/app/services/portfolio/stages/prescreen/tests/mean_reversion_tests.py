import numpy as np
import pandas as pd

# === Mean-Reversion Heuristic Tests Engine ===

def autocorrelation_test(short_returns, long_returns, threshold: float) -> bool:
    """
    Test for mean-reversion using lag-1 autocorrelation of returns.

    Negative autocorrelation indicates mean-reverting behavior.

    Args:
        short_returns: list of floats, daily returns in short-term window
        long_returns: list of floats, daily returns in long-term window
        threshold: float, maximum acceptable autocorrelation (e.g., 0 or -0.05)

    Returns:
        bool: True if either short-term or long-term autocorrelation <= threshold
    """
    results = []

    for returns in [short_returns, long_returns]:
        if len(returns) < 2:
            # Insufficient data; assume no autocorrelation
            results.append(1.0)
        else:
            # Compute lag-1 autocorrelation
            r1 = returns[:-1]
            r2 = returns[1:]
            autocorr = np.corrcoef(r1, r2)[0, 1]
            results.append(autocorr)

    return results[0] <= threshold or results[1] <= threshold


def zscore_reversion_test(
    data,
    short_start,
    long_start,
    window: int = 20,
    lookahead: int = 5,
    z_threshold: float = 2.0,
    threshold: float = 0.5
) -> bool:
    """
    Test mean-reversion using Z-score deviations from a rolling mean.

    For each period, measures how often prices revert toward the moving average
    within a lookahead window after deviating beyond `z_threshold`.

    Args:
        data: list of dicts with keys ['date', 'close']
        short_start: datetime, start of short-term period
        long_start: datetime, start of long-term period
        window: int, rolling window size for mean/std
        lookahead: int, number of days to check for reversion
        z_threshold: float, Z-score deviation defining extreme movement
        threshold: float, minimum proportion of reversions required (0–1)

    Returns:
        bool: True if reversion rate >= threshold in short or long period
    """
    # Convert to DataFrame and compute rolling stats
    df = pd.DataFrame(data).sort_values("date")
    df["mean"] = df["close"].rolling(window).mean()
    df["std"] = df["close"].rolling(window).std()
    df["zscore"] = (df["close"] - df["mean"]) / df["std"]

    long_extreme = long_revert = 0
    short_extreme = short_revert = 0

    for i in range(len(df) - lookahead):
        date = df["date"].iloc[i]
        z = df["zscore"].iloc[i]

        if np.isnan(z):
            continue

        if abs(z) > z_threshold:
            future_prices = df["close"].iloc[i+1:i+lookahead+1].values
            current_mean = df["mean"].iloc[i]

            reverted = (
                (z > 0 and np.any(future_prices < current_mean)) or
                (z < 0 and np.any(future_prices > current_mean))
            )

            # Long-term period
            if date >= long_start:
                long_extreme += 1
                if reverted:
                    long_revert += 1

            # Short-term period
            if date >= short_start:
                short_extreme += 1
                if reverted:
                    short_revert += 1

    # Compute reversion rates
    long_rate = long_revert / long_extreme * 100 if long_extreme > 0 else 0
    short_rate = short_revert / short_extreme * 100 if short_extreme > 0 else 0

    return long_rate >= threshold or short_rate >= threshold
