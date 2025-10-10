import numpy as np
import pandas as pd

def autocorrelation_test(short_returns, long_returns, threshold):
    """
    Tests for mean reversion by computing lag-1 autocorrelation
    of daily returns in short- and long-term windows.
    Negative autocorrelation (below threshold) indicates mean-reverting behavior.

    Parameters:
        short_returns (list[float]): Daily returns in the short-term window.
        long_returns (list[float]): Daily returns in the long-term window.
        threshold (float): Maximum acceptable autocorrelation (e.g., 0 or -0.05).

    Returns:
        bool: True if either short or long autocorrelation <= threshold (mean-reverting).
    """

    results = []

    for returns in [short_returns, long_returns]:
        if len(returns) < 2:
            results.append(1)

        else:
        # lag-1 autocorrelation
            r1 = returns[:-1]
            r2 = returns[1:]
            autocorr = np.corrcoef(r1, r2)[0, 1]

            results.append(autocorr)

    return results[0] <= threshold or results[1] <= threshold



def zscore_reversion_test(data, short_start, long_start, window=20, lookahead=5, z_threshold=2.0, threshold=0.5):
    """
    Tests mean-reversion behavior using Z-score reversion logic.

    For each period (long and short), this test calculates how often the price
    reverts toward its moving average within a given lookahead window after
    deviating more than `z_threshold` standard deviations from it.

    Parameters:
        data (list[dict]): List of { 'date': datetime, 'close': float }.
        short_start (datetime): Start date for short-term analysis.
        long_start (datetime): Start date for long-term analysis.
        window (int): Rolling window size for mean/std calculation.
        lookahead (int): Number of days to check for reversion after a deviation.
        z_threshold (float): Z-score threshold for defining "extreme" deviation.
        threshold (float): Minimum proportion of reversions required to pass (0-1).

    Returns:
        bool: True if reversion rate >= threshold in either short or long period.
    """

    # Convert to DataFrame for rolling calculations
    df = pd.DataFrame(data).sort_values("date")
    df["mean"] = df["close"].rolling(window).mean()
    df["std"] = df["close"].rolling(window).std()
    df["zscore"] = (df["close"] - df["mean"]) / df["std"]

    long_extreme = long_revert = 0
    short_extreme = short_revert = 0

    for i in range(len(df) - lookahead):
        date = df["date"].iloc[i]
        z = df["zscore"].iloc[i]

        # Skip until rolling stats are valid
        if np.isnan(z):
            continue

        # Only count points beyond threshold
        if abs(z) > z_threshold:
            future_prices = df["close"].iloc[i+1:i+lookahead+1].values
            current_mean = df["mean"].iloc[i]

            reverted = (
                (z > 0 and np.any(future_prices < current_mean)) or
                (z < 0 and np.any(future_prices > current_mean))
            )

            # Long window
            if date >= long_start:
                long_extreme += 1
                if reverted:
                    long_revert += 1

            # Short window
            if date >= short_start:
                short_extreme += 1
                if reverted:
                    short_revert += 1

    # Compute reversion rates safely
    long_rate = long_revert / long_extreme * 100 if long_extreme > 0 else 0
    short_rate = short_revert / short_extreme * 100 if short_extreme > 0 else 0

    return long_rate >= threshold or short_rate >= threshold
