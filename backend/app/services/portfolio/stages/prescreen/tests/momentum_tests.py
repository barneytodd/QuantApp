import numpy as np

# === Momentum Heuristic Tests Engine ===

def above_MA_test(data, MA, short_start, long_start, threshold: float = 0.7) -> bool:
    """
    Test what percentage of time the price is above its moving average (MA)
    over short- and long-term periods.

    Args:
        data: list of dicts with keys ['date', 'close']
        MA: dict mapping date -> MA value
        short_start: datetime, start of short-term period
        long_start: datetime, start of long-term period
        threshold: float, fraction (0-1) of time price should be above MA

    Returns:
        bool: True if short-term or long-term percentage above MA >= threshold
    """
    short_results = {"above": 0, "below": 0}
    long_results = {"above": 0, "below": 0}

    for row in data:
        date = row["date"]
        if date not in MA or not MA[date]:
            continue

        result = "above" if row["close"] > MA[date] else "below"

        if date >= long_start:
            long_results[result] += 1
            if date >= short_start:
                short_results[result] += 1

    def safe_pct(a, b):
        return a / b if b != 0 else 0

    short_pct = safe_pct(short_results["above"], short_results["above"] + short_results["below"])
    long_pct = safe_pct(long_results["above"], long_results["above"] + long_results["below"])

    return short_pct >= threshold or long_pct >= threshold


def av_slope_test(MA, short_start, long_start, threshold: float, lookback: int = 20) -> bool:
    """
    Check that the moving average (MA) has a positive slope over time.

    Args:
        MA: dict or Series mapping date -> MA value
        short_start: datetime, start of short-term period
        long_start: datetime, start of long-term period
        threshold: float, minimum normalized slope (e.g., 0.005 for 0.5%)
        lookback: int, number of days between slope points

    Returns:
        bool: True if mean slope >= threshold for short or long period
    """
    sorted_items = sorted(MA.items(), key=lambda x: x[0])
    dates = [d for d, _ in sorted_items]
    values = [v for _, v in sorted_items]

    long_slopes, short_slopes = [], []

    for i in range(lookback, len(dates)):
        date = dates[i]
        prev = values[i - lookback]
        curr = values[i]

        if not prev:
            continue

        slope = (curr - prev) / prev

        if date >= long_start:
            long_slopes.append(slope)
            if date >= short_start:
                short_slopes.append(slope)

    mean_long = np.mean(long_slopes) if long_slopes else 0
    mean_short = np.mean(short_slopes) if short_slopes else 0

    return mean_long >= threshold or mean_short >= threshold


def pos_returns_test(short_returns, long_returns, threshold: float) -> bool:
    """
    Checks whether the percentage of positive daily returns exceeds a threshold.

    Args:
        short_returns: list of daily returns in short-term period
        long_returns: list of daily returns in long-term period
        threshold: float, minimum % positive returns (0-100)

    Returns:
        bool: True if short-term or long-term positive return % >= threshold
    """
    def pct_positive(returns):
        pos = sum(1 for r in returns if r > 0)
        return (pos / len(returns) * 100) if returns else 0

    return pct_positive(short_returns) >= threshold or pct_positive(long_returns) >= threshold


def min_volatility_test(short_vol: float, long_vol: float, threshold: float) -> bool:
    """
    Passes if either short-term or long-term volatility exceeds the threshold.

    Args:
        short_vol: float, annualized short-term volatility
        long_vol: float, annualized long-term volatility
        threshold: float, minimum acceptable volatility

    Returns:
        bool: True if short_vol >= threshold or long_vol >= threshold
    """
    return short_vol >= threshold or long_vol >= threshold
