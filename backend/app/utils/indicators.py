from math import sqrt
import pandas as pd

# ================================
# Simple Moving Average (SMA)
# ================================
def compute_sma_matrix(price_matrix: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Vectorized SMA for all symbols.
    """
    return price_matrix.rolling(window=period, min_periods=period).mean()


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
def compute_bollinger_bands_matrix(price_matrix: pd.DataFrame, period: int, std_dev: float):
    """
    Vectorized Bollinger Bands for all symbols.
    
    Returns a dict of DataFrames: {'upper', 'middle', 'lower'}
    """
    middle = compute_sma_matrix(price_matrix, period)
    rolling_std = price_matrix.rolling(window=period, min_periods=period).std()
    
    upper = middle + std_dev * rolling_std
    lower = middle - std_dev * rolling_std
    
    return {"upper": upper, "middle": middle, "lower": lower}


# ================================
# Exponential Moving Average (EMA)
# ================================
def compute_ema_matrix(price_matrix: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Vectorized EMA for all symbols.
    """
    return price_matrix.ewm(span=period, adjust=False).mean()


# ================================
# Relative Strength Index (RSI)
# ================================
def compute_rsi_matrix(price_matrix: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Vectorized RSI using Wilder's smoothing for all symbols.
    """
    delta = price_matrix.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)
