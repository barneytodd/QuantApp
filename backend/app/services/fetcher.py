# Fetch data

import yfinance as yf
import pandas as pd
from datetime import datetime
from yahooquery import Screener
from yfinance import EquityQuery, screen
import time
from typing import List

# Fetch historical price data from Yahoo Finance
def fetch_historical(symbols: List[str], period: str = "1y", interval: str = "1d"):
    df = yf.download(symbols, period=period, interval=interval, progress=False, threads=False, group_by='ticker')
    if df.empty:
        return []
    records = []
    if isinstance(df.columns, pd.MultiIndex):
        print(df.head())
        for symbol in df.columns.levels[0]:
            sub_df = df[symbol].copy().reset_index()
            for _, row in sub_df.iterrows():
                records.append({
                    "symbol": symbol,
                    "date": row["Date"].date() if isinstance(row["Date"], pd.Timestamp) else row["Date"],
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
                })
    else:  # single symbol
        df = df.reset_index()
        symbol = symbols if isinstance(symbols, str) else symbols[0]
        for _, row in df.iterrows():
            records.append({
                "symbol": symbol,
                "date": row["Date"].date() if isinstance(row["Date"], pd.Timestamp) else row["Date"],
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
            })

    return records

# Fetch list of available symbols from Yahoo Finance based on criteria
def fetch_symbols(page_size=250, pause=0.3):
    all_symbols = []
    offset = 0

    query = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('is-in', ['exchange', 'NMS', 'NYQ']),
        EquityQuery('gt', ['lastclosemarketcap.lasttwelvemonths', 1_000_000_000]),
        EquityQuery('gt', ['avgdailyvol3m', 500_000]),
        EquityQuery('gt', ['epsgrowth.lasttwelvemonths', 0]),
        EquityQuery('lt', ['lastclosepriceearnings.lasttwelvemonths', 50])
    ])

    while True:
        results = screen(query=query, size=page_size, offset=offset)
        quotes = results.get("quotes", [])
        if not quotes:
            print("No more results returned.")
            break

        symbols = [q["symbol"] for q in quotes if "symbol" in q]
        all_symbols.extend(symbols)
        print(f"Fetched {len(symbols)} symbols (total {len(all_symbols)})")

        offset += page_size
        time.sleep(pause)  # polite delay to avoid rate-limiting

    all_symbols.sort()
    return all_symbols