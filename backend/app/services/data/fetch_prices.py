import contextlib
import io
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import yfinance as yf

from app.crud import upsert_prices, insert_missing_data
from app.database import SessionLocal
from app.schemas import PriceIn
from app.utils.data_helpers import chunk_symbols, get_missing_periods, get_symbol_date_ranges
from app.utils.yfinance_errors import safe_download



# === Historical Data Fetch & Ingestion Engine ===
def fetch_historical(symbols, period="1y", start=None, end=None, interval="1d", db=None):
    """
    Fetch OHLCV (Open, High, Low, Close, Volume) historical price data for one or more symbols
    using Yahoo Finance. Returns a list of dictionary records suitable for DB insertion.

    Args:
        symbols: single symbol or list of symbols
        period: string like '1y', ignored if start/end are provided
        start, end: optional date range (YYYY-MM-DD) for historical data
        interval: data granularity ('1d', '1h', etc.)
    Returns:
        List of dicts containing symbol, date, open, high, low, close, volume
    """
    all_records = []

    # --- Download data from Yahoo Finance ---
    if start and end:
        df = safe_download(
            symbols,
            db=db,
            start=start,
            end=end,
            interval=interval,
            progress=False,
            threads=True,
            group_by='ticker',
            auto_adjust=True
        )
        print(f"Fetched data for symbols: {symbols} from {start} to {end} with {len(df)} entries")
        if df.empty:
            return None
        
    else:
        df = safe_download(
            symbols,
            db=db,
            period=period,
            interval=interval,
            progress=False,
            threads=True,
            group_by='ticker',
            auto_adjust=True
        )

    # --- Handle multiple symbols (MultiIndex columns) ---
    if isinstance(df.columns, pd.MultiIndex):
        for symbol in df.columns.levels[0]:
            sub_df = df[symbol].copy().reset_index()
            sub_df['symbol'] = symbol
            sub_df['date'] = sub_df['Date'].dt.date
            sub_df['volume'] = sub_df['Volume'].fillna(0).astype(int)
            sub_df['open'] = sub_df['Open'].astype(float)
            sub_df['high'] = sub_df['High'].astype(float)
            sub_df['low'] = sub_df['Low'].astype(float)
            sub_df['close'] = sub_df['Close'].astype(float)
            all_records.extend(sub_df[['symbol','date','open','high','low','close','volume']].to_dict('records'))
    else:
        # --- Handle single symbol ---
        df = df.reset_index()
        symbol = symbols[0] if isinstance(symbols, list) else symbols
        df['symbol'] = symbol
        df['date'] = df['Date'].dt.date
        df['volume'] = df['Volume'].fillna(0).astype(int)
        df['open'] = df['Open'].astype(float)
        df['high'] = df['High'].astype(float)
        df['low'] = df['Low'].astype(float)
        df['close'] = df['Close'].astype(float)
        all_records.extend(df[['symbol','date','open','high','low','close','volume']].to_dict('records'))

    return all_records


def ingest_missing_data_parallel(db, symbols, start, end, chunk_size=50, max_workers=5):
    """
    Fetch missing OHLCV data for multiple symbols and insert into the DB in parallel.
    Uses ThreadPoolExecutor to process symbols concurrently.

    Args:
        db: SQLAlchemy Session
        symbols: list of stock symbols
        start, end: datetime.date objects for the range to ingest
        chunk_size: number of symbols processed per thread batch
        max_workers: number of parallel threads
    Returns:
        True if ingestion completes successfully
    """

    # --- Get existing date ranges for each symbol from DB ---
    ranges = get_symbol_date_ranges(db, symbols)

    # --- Compute missing periods for each symbol ---
    missing_periods = get_missing_periods(symbols, ranges, start, end)

    def fetch_and_insert(symbol):
        """
        Fetch missing periods for a single symbol and upsert into DB in chunks.
        """
        all_records = []
        with SessionLocal() as db_thread:
            for period_start, period_end in missing_periods.get(symbol, []):
                records = fetch_historical([symbol], start=str(period_start), end=str(period_end), db=db_thread)
                if records:
                    all_records.extend([PriceIn(**r) for r in records])

            if all_records:
                try:
                    upsert_prices(db_thread, all_records, chunk_size=500)
                    db_thread.commit()
                except Exception as e:
                    print(e)
                print(f"Inserted/Updated {len(all_records)} records for {symbol}")

    # --- Split symbols into chunks and process in parallel threads ---
    for chunk in chunk_symbols(list(missing_periods.keys()), chunk_size):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(fetch_and_insert, chunk)

    print("Data ingestion complete")
    return True
