from sqlalchemy.orm import Session
from app.crud import get_prices as crud_get_prices
from typing import Optional, List
import numpy as np
from sqlalchemy import func
from datetime import datetime, date, timedelta
from app.models.prices import Price



def fetch_price_data(db: Session, symbols: list[str], start: Optional[str] = None, end: Optional[str] = None, lookback: Optional[int] = 0):
    """Fetch OHLCV data from DB and convert to dict."""
    data_dict = {}
    for symbol in symbols:
        data_rows = crud_get_prices(db, [symbol], start, end, lookback)
        if not data_rows:
            continue
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

def convert_numpy(obj):
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
    Returns a dict: { symbol: (min_date, max_date) }
    """
    ranges = {}
    results = (
        db.query(
            Price.symbol,
            func.min(Price.date),
            func.max(Price.date)
        )
        .filter(Price.symbol.in_(symbols))
        .group_by(Price.symbol)
        .all()
    )
    for symbol, min_date, max_date in results:
        ranges[symbol] = (min_date, max_date)
    return ranges


def get_missing_periods(symbols, ranges, target_start, target_end):
    if isinstance(target_start, str):
        target_start = datetime.strptime(target_start, "%Y-%m-%d").date()
    if isinstance(target_end, str):
        target_end = datetime.strptime(target_end, "%Y-%m-%d").date()

    missing = {}
    for symbol in symbols:
        missing[symbol] = []
        if symbol not in ranges:
            missing[symbol].append((target_start, target_end))  # fetch full history
        else:
            db_start, db_end = ranges[symbol]
            # only fetch missing start or end
            if db_start > target_start:
                if target_start + timedelta(days=3) < db_start:
                    missing[symbol].append((target_start, db_start))
            if db_end < target_end:
                if db_end + timedelta(days=3) < target_end:
                    missing[symbol].append((db_end + timedelta(days=1), target_end + timedelta(days=1)))
    return missing


def chunk_symbols(symbols, chunk_size=50):
    for i in range(0, len(symbols), chunk_size):
        yield symbols[i:i+chunk_size]
