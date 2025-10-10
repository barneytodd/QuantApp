from math import sqrt

# Simple Moving Average
def compute_sma(data, period):
    result = []
    closes = [d["close"] for d in data]
    print(f"closes: {len(closes)}")
    dates = [d["date"] for d in data]
    for i in range(len(closes)):
        if i < period - 1:
            result.append({"date": dates[i], "value": None})
        else:
            window = closes[i - period + 1:i + 1]
            result.append({"date": dates[i], "value": sum(window) / period})
    return result

# Bollinger Bands
def compute_bollinger_bands(data, period, std_dev):
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

# Exponential Moving Average
def compute_ema(values, period):
    result = []
    k = 2 / (period + 1)  # smoothing factor
    ema_prev = None
    for i, v in enumerate(values):
        if v is None:
            result.append({"value": None})
            continue
        if ema_prev is None:
            # Start EMA with SMA of first 'period' values
            if i < period - 1:
                result.append({"value": None})
                continue
            window = [x for x in values[i - period + 1:i + 1] if x is not None]
            ema_prev = sum(window) / period
        else:
            ema_prev = v * k + ema_prev * (1 - k)
        result.append({"value": ema_prev})
    return result


# Relative Strength Index
def compute_rsi(data, period):
    closes = [d["close"] for d in data]
    deltas = [0] + [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    result = [None]  # first value has no RSI

    gain = lambda x: max(x, 0)
    loss = lambda x: -min(x, 0)

    avg_gain = sum(gain(d) for d in deltas[:period]) / period
    avg_loss = sum(loss(d) for d in deltas[:period]) / period

    rsi_series = [None] * period
    for i in range(period, len(deltas)):
        delta = deltas[i]
        avg_gain = (avg_gain * (period - 1) + gain(delta)) / period
        avg_loss = (avg_loss * (period - 1) + loss(delta)) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        rsi_series.append(rsi)
    return [{"value": val} if val is not None else {"value": None} for val in rsi_series]
