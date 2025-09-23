from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.prices import Price
from app.schemas.prices import PriceIn
from datetime import date

# Get historical OHLCV data for a symbol, optionally filtered by date range
def get_prices(db: Session, symbol: str, start: Optional[date] = None, end: Optional[date] = None) -> List[Price]:
    query = db.query(Price).filter(Price.symbol == symbol)
    if start:
        query = query.filter(Price.date >= start)
    if end:
        query = query.filter(Price.date <= end)
    return query.order_by(Price.date.asc()).all()

# Upsert a list of PriceIn records into the database
def upsert_prices(db: Session, price_list: List[PriceIn]):
    for price in price_list:
        db_price = db.query(Price).filter(
            Price.symbol == price.symbol,
            Price.date == price.date
        ).first()
        if db_price:
            # update existing
            db_price.open = price.open
            db_price.high = price.high
            db_price.low = price.low
            db_price.close = price.close
            db_price.volume = price.volume
        else:
            # insert new
            db.add(Price(**price.dict()))
    db.commit()
