from sqlalchemy.orm import Session
from app.crud import get_prices as crud_get_prices
from typing import Optional 

def fetch_price_data(db: Session, symbol: str, start: Optional[str] = None, end: Optional[str] = None):
    """Fetch OHLCV data from DB and convert to dict."""
    data_rows = crud_get_prices(db, symbol, start, end)
    if not data_rows:
        return None
    return [
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
