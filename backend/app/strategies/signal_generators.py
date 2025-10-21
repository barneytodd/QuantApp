from app.utils.indicators import compute_sma, compute_bollinger_bands, compute_rsi, compute_ema

# ===============================
# Simple Moving Average (SMA)
# ===============================
def sma_signal_generator(data, i, params):
    """Generate SMA crossover signals."""
    short, long = params["shortPeriod"], params["longPeriod"]
    if i < long:
        return "hold"

    short_val = compute_sma(data, short)[i]["value"]
    long_val = compute_sma(data, long)[i]["value"]
    if short_val is None or long_val is None:
        return "hold"

    if short_val > long_val:
        return "buy"
    if short_val < long_val:
        return "sell"
    return "hold"


# ===============================
# Bollinger Bands
# ===============================
def bollinger_signal_generator(data, i, params):
    """Generate signals based on Bollinger Band breakouts."""
    period, std_dev = params["period"], params["bandMultiplier"]
    bands = compute_bollinger_bands(data, period, std_dev)
    price = data[i]["close"]

    if bands[i]["lower"] is None or bands[i]["upper"] is None:
        return "hold"

    if price < bands[i]["lower"]:
        return "buy"
    if price > bands[i]["upper"]:
        return "sell"
    return "hold"


# ===============================
# Relative Strength Index (RSI)
# ===============================
def rsi_signal_generator(data, i, params):
    """Generate RSI overbought/oversold signals with optional smoothing."""
    period = params["period"]
    oversold = params["oversold"]
    overbought = params["overbought"]
    smoothing = params.get("signalSmoothing", 1)

    rsi_series = compute_rsi(data, period)
    rsi_values = [r["value"] for r in rsi_series]

    if smoothing > 1:
        smoothed_rsi_series = compute_ema(rsi_values, smoothing)
        rsi = smoothed_rsi_series[i]["value"]
    else:
        rsi = rsi_values[i]

    if rsi is None:
        return "hold"
    if rsi < oversold:
        return "buy"
    if rsi > overbought:
        return "sell"
    return "hold"


# ===============================
# Momentum
# ===============================
def momentum_signal_generator(data, i, params):
    """Generate momentum signals based on price change over lookback."""
    lookback = params["lookback"]
    if i < lookback:
        return "hold"

    past, current = data[i - lookback]["close"], data[i]["close"]
    if current > past:
        return "buy"
    if current < past:
        return "sell"
    return "hold"


# ===============================
# Breakout
# ===============================
def breakout_signal_generator(data, i, params):
    """Generate breakout signals based on price range and multiplier."""
    lookback, multiplier = params["lookback"], params["breakoutMultiplier"]
    if i < lookback:
        return "hold"

    window = data[i - lookback:i]
    values = [d["close"] for d in window]
    max_high, min_low = max(values), min(values)
    price = data[i]["close"]
    rnge = max_high - min_low

    if price > max_high + multiplier * rnge:
        return "buy"
    if price < min_low - multiplier * rnge:
        return "sell"
    return "hold"


# ===============================
# Pairs Trading
# ===============================
def pairs_signal_generator(data, i, params):
    """
    Generate signals for pairs trading based on z-score of spread.

    Returns:
        - "long": long first stock, short second
        - "short": short first stock, long second
        - "exit": close positions
        - "hold": no action
    """
    lookback, entryZ, exitZ = params["lookback"], params["entryZ"], params["exitZ"]
    stock1, stock2 = data.columns.tolist()[1:]

    if i < lookback:
        return "hold"

    price1, price2 = data[stock1].iloc[i], data[stock2].iloc[i]

    # Compute rolling spread statistics
    spread_series = [data[stock1].iloc[j] - data[stock2].iloc[j] for j in range(i - lookback, i)]
    mean = sum(spread_series) / lookback
    std = (sum((x - mean) ** 2 for x in spread_series) / lookback) ** 0.5

    z = (price1 - price2 - mean) / std if std != 0 else 0

    if z > entryZ:
        return "short"
    if z < -entryZ:
        return "long"
    if abs(z) < exitZ:
        return "exit"
    return "hold"
