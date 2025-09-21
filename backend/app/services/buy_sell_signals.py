from app.utils.indicators import compute_sma, compute_bollinger_bands, compute_rsi

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
    period, std_dev = params["period"], params["stdDev"]
    bands = compute_bollinger_bands(data, period, std_dev)
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
    period, oversold, overbought = params["period"], params["oversold"], params["overbought"]
    rsi_series = compute_rsi(data, period)
    rsi = rsi_series[i]["value"]
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
    lookback = params["lookback"]
    if i < lookback:
        return "hold"
    window = data[i - lookback:i]
    highs = [d["close"] for d in window]
    lows = [d["close"] for d in window]
    max_high, min_low = max(highs), min(lows)
    price = data[i]["close"]
    if price > max_high:
        return "buy"
    if price < min_low:
        return "sell"
    return "hold"

# Pairs Trading Signal Generator
def pairs_signal_generator(data, i, params):
    s1, s2 = params["symbol1"], params["symbol2"]
    lookback, entryZ, exitZ = params["lookback"], params["entryZ"], params["exitZ"]
    if i < lookback:
        return "hold"
    price1, price2 = data[i][s1], data[i][s2]
    spread_series = [data[j][s1] - data[j][s2] for j in range(i - lookback, i)]
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
