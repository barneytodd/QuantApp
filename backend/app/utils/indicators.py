from math import sqrt

# ================================
# Simple Moving Average (SMA)
# ================================
def compute_sma(data, period):
    """
    Computes the Simple Moving Average (SMA) for a given period.

    Parameters:
        data (list[dict]): List of dicts with keys 'date' and 'close'.
        period (int): Lookback period for the SMA calculation.

    Returns:
        list[dict]: Each element is a dict with:
            - 'date': corresponding date
            - 'value': SMA value (None for initial periods where SMA cannot be computed)
    """
    result = []
    closes = [d["close"] for d in data]
    dates = [d["date"] for d in data]

    for i in range(len(closes)):
        if i < period - 1:
            result.append({"date": dates[i], "value": None})  # Not enough data for SMA
        else:
            window = closes[i - period + 1:i + 1]
            sma_val = sum(window) / period
            result.append({"date": dates[i], "value": sma_val})
    return result


# ================================
# Bollinger Bands
# ================================
def compute_bollinger_bands(data, period, std_dev):
    """
    Computes Bollinger Bands: upper, middle (SMA), and lower bands.

    Parameters:
        data (list[dict]): List of dicts with keys 'date' and 'close'.
        period (int): Lookback period for the moving average.
        std_dev (float): Number of standard deviations for upper/lower bands.

    Returns:
        list[dict]: Each element contains:
            - 'upper': Upper band
            - 'middle': Middle band (SMA)
            - 'lower': Lower band
            Initial periods return None for bands until enough data is available.
    """
    closes = [d["close"] for d in data]
    result = []

    for i in range(len(closes)):
        if i < period - 1:
            result.append({"upper": None, "middle": None, "lower": None})
        else:
            window = closes[i - period + 1:i + 1]
            mean = sum(window) / period
            variance = sum((x - mean) ** 2 for x in window) / period
            sd = sqrt(variance)
            result.append({
                "upper": mean + std_dev * sd,
                "middle": mean,
                "lower": mean - std_dev * sd
            })
    return result


# ================================
# Exponential Moving Average (EMA)
# ================================
def compute_ema(values, period):
    """
    Computes the Exponential Moving Average (EMA) for a series of values.

    Parameters:
        values (list[float or None]): Series of numeric values.
        period (int): Lookback period for EMA calculation.

    Returns:
        list[dict]: Each element is a dict with key 'value', the EMA.
                    Initial periods or None values produce 'value': None.
    """
    result = []
    k = 2 / (period + 1)  # Smoothing factor
    ema_prev = None

    for i, v in enumerate(values):
        if v is None:
            result.append({"value": None})
            continue

        if ema_prev is None:
            # Initialize EMA using SMA of first 'period' values
            if i < period - 1:
                result.append({"value": None})
                continue
            window = [x for x in values[i - period + 1:i + 1] if x is not None]
            ema_prev = sum(window) / period
        else:
            # EMA formula: EMA_today = value * k + EMA_yesterday * (1 - k)
            ema_prev = v * k + ema_prev * (1 - k)

        result.append({"value": ema_prev})
    return result


# ================================
# Relative Strength Index (RSI)
# ================================
def compute_rsi(data, period):
    """
    Computes the Relative Strength Index (RSI) for a given period.

    Parameters:
        data (list[dict]): List of dicts with key 'close'.
        period (int): Lookback period for RSI calculation.

    Returns:
        list[dict]: Each element is a dict with 'value' (RSI). 
                    Initial periods where RSI cannot be computed have 'value': None.

    Notes:
        - RSI measures momentum: values >70 indicate overbought, <30 indicate oversold.
        - Uses Wilder's smoothing method for average gains/losses.
    """
    closes = [d["close"] for d in data]
    deltas = [0] + [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    rsi_series = [None] * period  # First 'period' values cannot have RSI

    # Lambda functions to extract gains and losses
    gain = lambda x: max(x, 0)
    loss = lambda x: -min(x, 0)

    # Initial average gain/loss
    avg_gain = sum(gain(d) for d in deltas[:period]) / period
    avg_loss = sum(loss(d) for d in deltas[:period]) / period

    for i in range(period, len(deltas)):
        delta = deltas[i]
        avg_gain = (avg_gain * (period - 1) + gain(delta)) / period
        avg_loss = (avg_loss * (period - 1) + loss(delta)) / period

        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        rsi_series.append(rsi)

    return [{"value": val} if val is not None else {"value": None} for val in rsi_series]
