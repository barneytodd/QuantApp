import numpy as np
from scipy.stats import skew, kurtosis

import numpy as np

def bid_ask_test(data, short_start, long_start, threshold=0.005):
    """
    Checks if the average bid-ask spread (high-low)/close
    is below a threshold for both long and short periods.

    data: list of dicts with keys ['date', 'high', 'low', 'close']
    short_start, long_start: datetime thresholds
    threshold: max acceptable average spread (e.g., 0.005 = 0.5%)
    """
    short_spreads = []
    long_spreads = []

    for row in data:
        date = row["date"]
        close = row.get("close")
        high = row.get("high")
        low = row.get("low")

        if close is None or close == 0 or np.isnan(close):
            continue

        if date >= long_start:
            spread = (high - low) / close
            long_spreads.append(spread)

            if date >= short_start:
                short_spreads.append(spread)

    def safe_mean(values):
        return float(np.mean(values)) if values else np.nan

    short_mean = safe_mean(short_spreads)
    long_mean = safe_mean(long_spreads)

    return (
        (not np.isnan(short_mean) and short_mean <= threshold)
        or (not np.isnan(long_mean) and long_mean <= threshold)
    )



def max_drawdown_test(data, long_start, threshold=0.3):
    """
    Computes the maximum drawdown (as a fraction, e.g. 0.2 = 20%)
    over the period since `long_start`.

    data: list of dicts with keys ['date', 'close']
    long_start: datetime threshold for period start
    threshold: max acceptable drawdown
    """
    peak = None
    max_dd = 0.0

    for row in data:
        date = row["date"]
        if date < long_start:
            continue

        close = row["close"]
        if peak is None:
            peak = close
        else:
            peak = max(peak, close)

        if peak > 0:
            drawdown = (peak - close) / peak
            max_dd = max(max_dd, drawdown)

    return max_dd <= threshold

		


def skewness_test(short_returns, long_returns, threshold=0):
    """
    Tests skewness (asymmetry of return distribution).

    short_returns, long_returns: lists or arrays of returns
    threshold: minimum acceptable skewness (e.g., 0 for symmetric, >0 for right-skewed)
    """
    def safe_skew(x):
        return float(skew(x, bias=False)) if len(x) > 2 else np.nan

    short_skew = safe_skew(short_returns)
    long_skew = safe_skew(long_returns)

    return (
        (not np.isnan(short_skew) and short_skew >= threshold)
        or (not np.isnan(long_skew) and long_skew >= threshold)
    )



def kurtosis_test(short_returns, long_returns, threshold=3):
    """
    Tests kurtosis (tail heaviness) of return distributions.
    
    short_returns, long_returns: lists or arrays of returns
    threshold: maximum acceptable kurtosis
       - For Fisher=False (normal=3): use threshold=3-4
       - For Fisher=True (normal=0): use threshold=0-1
    """
    def safe_kurt(x):
        return float(kurtosis(x, fisher=False, bias=False)) if len(x) > 3 else np.nan

    short_kurt = safe_kurt(short_returns)
    long_kurt = safe_kurt(long_returns)

    return (
        (not np.isnan(short_kurt) and short_kurt <= threshold)
        or (not np.isnan(long_kurt) and long_kurt <= threshold)
    )


def max_volatility_test(short_vol, long_vol, threshold):
    """
    Passes if either short or long period volatility is below the threshold.

    short_vol, long_vol: annualized volatilities 
    threshold: max acceptable volatility 
    """
    return short_vol <= threshold or long_vol <= threshold
