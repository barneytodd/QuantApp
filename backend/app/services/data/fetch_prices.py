from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import yfinance as yf

from app.crud import upsert_prices
from app.database import SessionLocal
from app.schemas import PriceIn
from app.utils.data_helpers import chunk_symbols, get_missing_periods, get_symbol_date_ranges



# Fetch historical price data from Yahoo Finance
def fetch_historical(symbols, period="1y", start=None, end=None, interval="1d"):
    all_records = []
    if start and end:
        try:
            df = yf.download(symbols, start=start, end=end, interval=interval, progress=False, threads=True, group_by='ticker', auto_adjust=True)
            if df.empty:
                return None
        except Exception as e:
            return None
    else:
        df = yf.download(symbols, period=period, interval=interval, progress=False, threads=True, group_by='ticker', auto_adjust=True)

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
        # single symbol
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
    Fetch missing OHLCV data for a list of symbols and insert into the DB in parallel.
    
    Args:
        db: SQLAlchemy Session
        symbols: list of symbols
        start, end: datetime.date objects for the full range to ingest
        chunk_size: number of symbols per thread batch
        max_workers: number of parallel threads
    """
    # Get existing date ranges for symbols
    ranges = get_symbol_date_ranges(db, symbols)
    
    # Compute missing periods per symbol
    missing_periods = get_missing_periods(symbols, ranges, start, end)

    def fetch_and_insert(symbol):
        """Fetch missing periods for a symbol and insert into DB."""
        all_records = []
        with SessionLocal() as db_thread:
            for period_start, period_end in missing_periods.get(symbol, []):
                records = fetch_historical([symbol], start=str(period_start), end=str(period_end))
                if records:
                    all_records.extend([PriceIn(**r) for r in records])

            if all_records:
                upsert_prices(db_thread, all_records, chunk_size=500)
                db_thread.commit()
                print(f"Inserted/Updated {len(all_records)} records for {symbol}")

    # Chunk symbols and run in parallel
    for chunk in chunk_symbols(list(missing_periods.keys()), chunk_size):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(fetch_and_insert, chunk)
    print("Data ingestion complete")
    return True

