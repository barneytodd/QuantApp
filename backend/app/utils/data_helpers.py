from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import get_prices, get_prices_light
from app.models import Price, MissingPriceRange


def fetch_price_data(db: Session, symbols: list[str], start: Optional[str] = None, end: Optional[str] = None, lookback: Optional[int] = 0):
    """
    Fetch full OHLCV data for a list of symbols from the database.

    Parameters:
        db (Session): SQLAlchemy DB session
        symbols (list[str]): List of symbols to fetch
        start (str, optional): Start date in 'YYYY-MM-DD' format
        end (str, optional): End date in 'YYYY-MM-DD' format
        lookback (int, optional): Number of rows to fetch backwards from end (default 0)

    Returns:
        dict: { symbol: list of dicts with keys ['date', 'open', 'high', 'low', 'close', 'volume', 'symbol'] }
    """
    data_dict = {}
    for symbol in symbols:
        data_rows = get_prices(db, [symbol], start, end, lookback)
        if not data_rows:
            continue  # skip symbols with no data
        data_dict[symbol] = [
            {
                "date": r.date.isoformat(),
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "symbol": r.symbol,
            }
            for r in data_rows
        ]
    return data_dict


def fetch_price_data_light(db: Session, symbols: list[str], start: Optional[str] = None, end: Optional[str] = None, lookback: Optional[int] = 0):
    """
    Fetch lightweight OHLC data for a list of symbols from the database.
    Returns only 'high', 'low', 'close', and 'date'.

    Parameters:
        db (Session): SQLAlchemy DB session
        symbols (list[str]): List of symbols to fetch
        start (str, optional): Start date in 'YYYY-MM-DD' format
        end (str, optional): End date in 'YYYY-MM-DD' format
        lookback (int, optional): Number of rows to fetch backwards from end (default 0)

    Returns:
        dict: { symbol: list of dicts with keys ['date', 'high', 'low', 'close'] }
              Empty list if no data is available for symbol
    """
    data_dict = {}
    for symbol in symbols:
        data_rows = get_prices_light(db, [symbol], start, end, lookback)
        if not data_rows:
            data_dict[symbol] = []
        else:
            data_dict[symbol] = [
                {
                    "date": r["date"].isoformat(),
                    "high": r["high"],
                    "low": r["low"],
                    "close": r["close"],
                }
                for r in data_rows
            ]
    return data_dict


def convert_numpy(obj):
    """
    Recursively convert numpy data types to native Python types.
    Useful for JSON serialization of data containing numpy arrays or scalars.

    Parameters:
        obj: dict, list, tuple, np.ndarray, or numpy scalar

    Returns:
        Converted object with native Python types (int, float, list, tuple)
    """
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy(v) for v in obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def get_symbol_date_ranges(db, symbols: List[str]):
    """
    Query the database to get the earliest and latest available dates for each symbol.

    Parameters:
        db (Session): SQLAlchemy DB session
        symbols (List[str]): List of symbols to query

    Returns:
        dict: { symbol: (min_date, max_date) }
              Symbols not in DB are omitted
    """
    ranges = {}

    db_results = (
        db.query(
            Price.symbol,
            func.min(Price.date),
            func.max(Price.date)
        )
        .filter(Price.symbol.in_(symbols))
        .group_by(Price.symbol)
        .all()
    )

    missing_results = (
        db.query(
            MissingPriceRange.symbol,
            func.min(MissingPriceRange.start_date),
            func.max(MissingPriceRange.end_date)
        )
        .filter(MissingPriceRange.symbol.in_(symbols))
        .group_by(MissingPriceRange.symbol)
        .all()
    )

    for symbol, min_date, max_date in db_results:
        ranges[symbol] = (min_date, max_date)

    for symbol, missing_min, missing_max in missing_results:
        if symbol in ranges:
            current_min, current_max = ranges[symbol]
            overall_min = min(current_min, missing_min)
            overall_max = max(current_max, missing_max)
            ranges[symbol] = (overall_min, overall_max)
        else:
            ranges[symbol] = (missing_min, missing_max)

    return ranges


def get_missing_periods(symbols, ranges, target_start, target_end):
    """
    Compute periods for which historical data is missing for each symbol.

    Parameters:
        symbols (list[str]): Symbols to check
        ranges (dict): Output from `get_symbol_date_ranges`
        target_start (str or datetime.date): Desired start date
        target_end (str or datetime.date): Desired end date

    Returns:
        dict: { symbol: list of (start_date, end_date) tuples representing missing periods }
    """
    if isinstance(target_start, str):
        target_start = datetime.strptime(target_start, "%Y-%m-%d").date()
    if isinstance(target_end, str):
        target_end = datetime.strptime(target_end, "%Y-%m-%d").date()

    missing = {}
    for symbol in symbols:
        missing[symbol] = []
        if symbol not in ranges:
            # Symbol missing entirely from DB
            missing[symbol].append((target_start, target_end))
        else:
            db_start, db_end = ranges[symbol]
            # Missing data at start
            if db_start > target_start:
                if target_start + timedelta(days=3) < db_start:  # 3-day buffer
                    missing[symbol].append((target_start, db_start))
            # Missing data at end
            if db_end < target_end:
                if db_end + timedelta(days=3) < target_end:  # 3-day buffer
                    missing[symbol].append((db_end + timedelta(days=1), target_end + timedelta(days=1)))
    return missing


def chunk_symbols(symbols, chunk_size=50):
    """
    Yield successive chunks of symbols for batch processing.

    Parameters:
        symbols (list): List of symbols
        chunk_size (int): Maximum number of symbols per batch

    Yields:
        list: Next batch of symbols
    """
    for i in range(0, len(symbols), chunk_size):
        yield symbols[i:i + chunk_size]
