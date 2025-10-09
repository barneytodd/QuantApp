def above_MA_test(data, MA, short_start, long_start, threshold=0.7):
    """
    Tests what % of time price is above MA over long and short periods.

    data: list of dicts with keys ['date', 'close']
    MA: dict mapping date -> MA value
    short_start, long_start: datetime thresholds
    threshold: fraction (e.g., 0.7 means 70%)
    """
    short_results = {"above": 0, "below": 0}
    long_results = {"above": 0, "below": 0}

    for row in data:
        date = row["date"]
        if date not in MA:
            continue

        if date >= long_start:
            result = "above" if row["close"] > MA[date] else "below"
            long_results[result] += 1

            if date >= short_start:
                short_results[result] += 1

    def safe_ratio(a, b):
        return a / b if b != 0 else 0

    short_pct = safe_ratio(short_results["above"], short_results["above"] + short_results["below"])
    long_pct = safe_ratio(long_results["above"], long_results["above"] + long_results["below"])

    return (short_pct >= threshold) or (long_pct >= threshold)



def av_slope_test(MA, short_start, long_start, threshold, lookback=20):
    """
    MA: dict or Series mapping date -> MA value
    short_start, long_start: datetime or comparable date thresholds
    threshold: min normalized slope (e.g. 0.005 for 0.5%)
    lookback: days between slope points
    """
    # Sort by date
    sorted_items = sorted(MA.items(), key=lambda x: x[0])
    dates = [d for d, _ in sorted_items]
    values = [v for _, v in sorted_items]

    long_slopes, short_slopes = [], []

    for i in range(lookback, len(dates)):
        date = dates[i]
        close = values[i]
        prev_close = values[i - lookback]
        if prev_close == 0 or np.isnan(prev_close):
            continue
        slope = (close - prev_close) / prev_close

        # Long period slope accumulation
        if date >= long_start:
            long_slopes.append(slope)
            # Short period subset
            if date >= short_start:
                short_slopes.append(slope)

    mean_long = np.mean(long_slopes) if long_slopes else 0
    mean_short = np.mean(short_slopes) if short_slopes else 0

    return mean_long >= threshold or mean_short >= threshold


def pos_returns_test(data, short_start, long_start, threshold):
    """
    Checks whether the percentage of positive daily returns
    exceeds a threshold in either short or long lookback periods.
    """
    long_results = {"pos": 0, "neg": 0}
    short_results = {"pos": 0, "neg": 0}

    dates = [row["date"] for row in data]
    values = [row["close"] for row in data]

    for i in range(1, len(dates)):
        date = dates[i-1]
        if date >= long_start:
            retrn = values[i] - values[i-1]
            direction = "pos" if retrn > 0 else "neg"
            long_results[direction] += 1
            if date >= short_start:
                short_results[direction] += 1

    long_pct = long_results["pos"] / (long_results["pos"] + long_results["neg"])
    short_pct = short_results["pos"] / (short_results["pos"] + short_results["neg"])

    return long_pct >= threshold or short_pct >= threshold


def min_volatility_test(short_vol, long_vol, threshold):
    """Passes if either short or long period volatility is above the threshold."""
    return short_vol >= threshold or long_vol >= threshold