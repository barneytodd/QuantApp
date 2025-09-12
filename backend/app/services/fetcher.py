# Fetch data

import yfinance as yf
import pandas as pd
from datetime import datetime

# Fetch historical price data from Yahoo Finance
def fetch_historical(symbol: str, period: str = "1y", interval: str = "1d"):
    df = yf.download(symbol, period=period, interval=interval, progress=False, threads=False)
    if df.empty:
        return []
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.reset_index()
    records = []
    for _, row in df.iterrows():
        records.append({
            "symbol": symbol,
            "date": row["Date"].date() if isinstance(row["Date"], (pd.Timestamp, datetime)) else row["Date"],
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
        })
    return records
