from sqlalchemy.orm import Session
from app.crud import get_prices as crud_get_prices
from typing import Optional, List
import numpy as np

def fetch_price_data(db: Session, symbols: list[str], start: Optional[str] = None, end: Optional[str] = None):
    """Fetch OHLCV data from DB and convert to dict."""
    data_dict = {}
    for symbol in symbols:
        data_rows = crud_get_prices(db, symbol, start, end)
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
