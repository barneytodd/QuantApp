import numpy as np
from scipy.stats import skew, kurtosis

# === Global Heuristic Tests Engine ===

def bid_ask_test(data, short_start, long_start, threshold=0.005) -> bool:
    """
    Check if the average bid-ask spread is below a threshold.

    Args:
        data: list of dicts with keys ['date', 'high', 'low', 'close']
        short_start: datetime, start date for short-term period
        long_start: datetime, start date for long-term period
        threshold: float, max acceptable average spread (e.g., 0.005 = 0.5%)

    Returns:
        bool: True if short-term or long-term average spread <= threshold
    """
    short_spreads, long_spreads = [], []

    for row in data:
        date = row["date"]
        close = row.get("close")
        high = row.get("high")
        low = row.get("low")

        if close is None or close == 0 or np.isnan(close):
            continue

        spread = (high - low) / close

        if date >= long_start:
            long_spreads.append(spread)
            if date >= short_start:
                short_spreads.append(spread)

    def safe_mean(values):
        return float(np.mean(values)) if values else np.nan

    short_mean = safe_mean(short_spreads)
    long_mean = safe_mean(long_spreads)

    return (not np.isnan(short_mean) and short_mean <= threshold) or \
           (not np.isnan(long_mean) and long_mean <= threshold)


def max_drawdown_test(data, long_start, threshold=0.3) -> bool:
    """
    Compute maximum drawdown and check if it is within acceptable limits.

    Args:
        data: list of dicts with keys ['date', 'close']
        long_start: datetime, period start date
        threshold: float, maximum acceptable drawdown (fraction, e.g., 0.2 = 20%)

    Returns:
        bool: True if max drawdown <= threshold
    """
    peak, max_dd = None, 0.0

    for row in data:
        date = row["date"]
        if date < long_start:
            continue

        close = row["close"]
        peak = close if peak is None else max(peak, close)

        if peak > 0:
            drawdown = (peak - close) / peak
            max_dd = max(max_dd, drawdown)

    return max_dd <= threshold


def skewness_test(short_returns, long_returns, threshold=0) -> bool:
    """
    Check skewness of return distributions.

    Args:
        short_returns, long_returns: lists or arrays of returns
        threshold: minimum acceptable skewness (0 = symmetric)

    Returns:
        bool: True if skewness >= threshold for short or long period
    """
    def safe_skew(x):
        return float(skew(x, bias=False)) if len(x) > 2 else np.nan

    short_skew = safe_skew(short_returns)
    long_skew = safe_skew(long_returns)

    return (not np.isnan(short_skew) and short_skew >= threshold) or \
           (not np.isnan(long_skew) and long_skew >= threshold)


def kurtosis_test(short_returns, long_returns, threshold=3) -> bool:
    """
    Check kurtosis (tail heaviness) of return distributions.

    Args:
        short_returns, long_returns: lists or arrays of returns
        threshold: max acceptable kurtosis (Fisher=False, normal=3)

    Returns:
        bool: True if kurtosis <= threshold for short or long period
    """
    def safe_kurt(x):
        return float(kurtosis(x, fisher=False, bias=False)) if len(x) > 3 else np.nan

    short_kurt = safe_kurt(short_returns)
    long_kurt = safe_kurt(long_returns)

    return (not np.isnan(short_kurt) and short_kurt <= threshold) or \
           (not np.isnan(long_kurt) and long_kurt <= threshold)


def max_volatility_test(short_vol, long_vol, threshold) -> bool:
    """
    Check if annualized volatility is below a threshold.

    Args:
        short_vol, long_vol: float, annualized volatilities
        threshold: float, max acceptable volatility

    Returns:
        bool: True if short or long period volatility <= threshold
    """
    return short_vol <= threshold or long_vol <= threshold
