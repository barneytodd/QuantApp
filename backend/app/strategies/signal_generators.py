from app.utils.indicators import compute_sma, compute_bollinger_bands, compute_rsi, compute_ema

# SMA Signal Generator
def sma_signal_generator(data, i, params):
    short, long = params["shortPeriod"], params["longPeriod"]
    if i < long:
        return "hold"
    short_val = compute_sma(data, short)[i]["value"]
    long_val = compute_sma(data, long)[i]["value"]
    if not short_val or not long_val:
        return "hold"
    if short_val > long_val:
        return "buy"
    if short_val < long_val:
        return "sell"
    return "hold"

# Bollinger Bands Signal Generator
def bollinger_signal_generator(data, i, params):
    period, std_dev, bollinger_multiplier = params["period"], params["stdDev"], params["bollingerMultiplier"]
    bands = compute_bollinger_bands(data, period, std_dev*bollinger_multiplier)
    price = data[i]["close"]
    if not bands[i]["lower"] or not bands[i]["upper"]:
        return "hold"
    if price < bands[i]["lower"]:
        return "buy"
    if price > bands[i]["upper"]:
        return "sell"
    return "hold"

# RSI Signal Generator
def rsi_signal_generator(data, i, params):
    period, oversold, overbought, smoothing = params["period"], params["oversold"], params["overbought"], params["signalSmoothing"]
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

# Momentum Signal Generator
def momentum_signal_generator(data, i, params):
    lookback = params["lookback"]
    if i < lookback:
        return "hold"
    past, current = data[i - lookback]["close"], data[i]["close"]
    if current > past:
        return "buy"
    if current < past:
        return "sell"
    return "hold"

# Breakout Signal Generator
def breakout_signal_generator(data, i, params):
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

# Pairs Trading Signal Generator
def pairs_signal_generator(data, i, params):
 
    lookback, entryZ, exitZ, stock1, stock2 = params["lookback"], params["entryZ"], params["exitZ"], params["stock1"], params["stock2"]

    if i < lookback:
        return "hold"

    price1, price2 = data[i][stock1], data[i][stock2]

    # compute spread series for rolling window
    spread_series = [data[j][stock1] - data[j][stock2] for j in range(i - lookback, i)]
    mean = sum(spread_series) / lookback
    std = (sum((x - mean) ** 2 for x in spread_series) / lookback) ** 0.5

    # z-score of current spread
    z = (price1 - price2 - mean) / std if std != 0 else 0

    if z > entryZ:
        return "short"   # spread too wide - short stock1, long stock2
    if z < -entryZ:
        return "long"    # spread too narrow - long stock1, short stock2
    if abs(z) < exitZ:
        return "exit"    # spread normalized - exit positions
    return "hold"
