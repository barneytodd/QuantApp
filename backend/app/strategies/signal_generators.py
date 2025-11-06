import numpy as np
import pandas as pd

from app.utils.indicators import compute_sma_matrix, compute_bollinger_bands_matrix, compute_rsi_matrix, compute_ema_matrix

# ===============================
# Simple Moving Average (SMA)
# ===============================
def sma_signal_generator(price_matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Compute SMA crossover signals for all symbols in price_matrix.
    
    Returns a DataFrame with:
    1 = buy, 0 = exit, np.nan = hold
    """
    short = params.get("shortPeriod", 20)
    long = params.get("longPeriod", 50)
    sma_short = compute_sma_matrix(price_matrix, short)
    sma_long = compute_sma_matrix(price_matrix, long)
    
    signals = pd.DataFrame(np.nan, index=price_matrix.index, columns=price_matrix.columns)
    signals[sma_short > sma_long] = 1   # buy
    signals[sma_short < sma_long] = 0  # sell
    signals.iloc[-1] = 0 # force exit on last date
    return signals


# ===============================
# Bollinger Bands
# ===============================
def bollinger_signal_generator(price_matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Compute bollinger band signals for all symbols in price_matrix.
    
    Returns a DataFrame with:
    1 = buy, 0 = exit, np.nan = hold
    """
    period = params.get("period", 20)
    std_dev = params.get("bandMultiplier", 2)
    bands = compute_bollinger_bands_matrix(price_matrix, period, std_dev)
    signals = pd.DataFrame(np.nan, index=price_matrix.index, columns=price_matrix.columns)

    signals[price_matrix < bands["lower"]] = 1   # buy
    signals[price_matrix >= bands["lower"]] = 0  # sell
    signals.iloc[-1] = 0 # force exit on last date
    return signals


# ===============================
# Relative Strength Index (RSI)
# ===============================
def rsi_signal_generator(price_matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Compute RSI signals for all symbols in price_matrix.
    
    Returns a DataFrame with:
    1 = buy, 0 = exit, np.nan = hold
    """
    period = params.get("period", 14)
    oversold = params.get("oversold", 30)
    overbought = params.get("overbought", 70)
    smoothing = params.get("signalSmoothing", 1)

    rsi = compute_rsi_matrix(price_matrix, period)
    
    if smoothing > 1:
        rsi = compute_ema_matrix(rsi, smoothing)
    
    signals = pd.DataFrame(np.nan, index=price_matrix.index, columns=price_matrix.columns)
    signals[rsi < oversold] = 1   # buy
    signals[rsi >= oversold] = 0 # sell
    signals.iloc[-1] = 0 # force exit on last date
    return signals


# ===============================
# Momentum
# ===============================
def momentum_signal_generator(price_matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Compute momentum signals for all symbols in price_matrix.
    
    Returns a DataFrame with:
    1 = buy, 0 = exit, np.nan = hold
    """
    lookback = params.get("lookback", 126)

    shifted = price_matrix.shift(lookback)
    signals = pd.DataFrame(np.nan, index=price_matrix.index, columns=price_matrix.columns)
    signals[price_matrix > shifted] = 1
    signals[price_matrix < shifted] = 0
    signals.iloc[-1] = 0 # force exit on last date
    return signals


# ===============================
# Breakout
# ===============================
def breakout_signal_generator(price_matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Compute breakout signals for all symbols in price_matrix.
    
    Returns a DataFrame with:
    1 = buy, 0 = exit, np.nan = hold
    """
    lookback = params.get("lookback", 20)
    multiplier = params.get("breakoutMultiplier", 0.0)

    rolling_max = price_matrix.rolling(window=lookback).max()
    rolling_min = price_matrix.rolling(window=lookback).min()
    range_ = rolling_max - rolling_min
    
    signals = pd.DataFrame(np.nan, index=price_matrix.index, columns=price_matrix.columns)
    signals[price_matrix > rolling_max + multiplier * range_] = 1
    signals[price_matrix <= rolling_max + multiplier * range_] = 0
    signals.iloc[-1] = 0 # force exit on last date
    return signals


# ===============================
# Pairs Trading
# ===============================
def pairs_signal_generator(price_matrix: pd.DataFrame, stock1: str, stock2: str,
                            params: dict) -> pd.Series:
    """
    Vectorized pairs trading signal generator for a single stock pair.

    Args:
        price_matrix (pd.DataFrame): DataFrame with dates as index and symbols as columns.
        stock1 (str): First stock symbol
        stock2 (str): Second stock symbol
        lookback (int): Rolling window for z-score computation
        entry_z (float): Z-score threshold to enter positions
        exit_z (float): Z-score threshold to exit positions

    Returns:
        pd.Series: Signals for all dates
                   1 = long first, short second
                   -1 = short first, long second
                   0 = exit
                   np.nan = hold
    """
    lookback = params.get("lookback", 20)
    entry_z = params.get("entryZ", 2.0)
    exit_z = params.get("exitZ", 0.5)
    hedge_ratio = params.get("hedgeRatio", 1.0)

    # Compute rolling spread
    spread = price_matrix[stock1] - price_matrix[stock2]
    
    # Rolling mean and std
    spread_mean = spread.rolling(lookback).mean()
    spread_std = spread.rolling(lookback).std()
    
    # Z-score
    zscore = (spread - spread_mean) / spread_std
    
    # Initialize signals
    signals = pd.Series(np.nan, index=price_matrix.index, dtype=int)
    
    # Entry signals
    signals[zscore > entry_z] = -1   # short first, long second
    signals[zscore < -entry_z] = 1   # long first, short second
    
    # Exit signals
    signals[abs(zscore) < exit_z] = 0
    
    # First `lookback` days cannot have valid signals
    signals.iloc[:lookback] = 0

    signals.iloc[-1] = 0 # force exit on last date
    return signals


# ===============================
# Equal Weight
# ===============================
def equal_weight_signal_generator(price_matrix: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Compute equal weight signals for all symbols in price_matrix.
    
    Returns a DataFrame with:
    1 = buy, 0 = exit, np.nan = hold
    """
    signals = pd.DataFrame(1, index=price_matrix.index, columns=price_matrix.columns)
    signals.iloc[-1] = 0 # force exit on last date
    return signals