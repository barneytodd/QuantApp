# Define database logic - create, read, update, delete

from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
from typing import List

# Insert or update prices
def upsert_prices(db: Session, prices: List[schemas.PriceIn]):
    for p in prices:
        existing = db.query(models.Price).filter(models.Price.symbol == p.symbol, models.Price.date == p.date).first()
        if existing:
            # Update
            existing.open = p.open
            existing.high = p.high
            existing.low = p.low
            existing.close = p.close
            existing.volume = p.volume
        else:
            # Insert
            db.add(models.Price(**p.dict()))
    db.commit()

# Read prices for a specified ticker symbol between a specified date range
def get_prices(db: Session, symbol: str, start: date = None, end: date = None):
    q = db.query(models.Price).filter(models.Price.symbol == symbol)
    if start:
        q = q.filter(models.Price.date >= start)
    if end:
        q = q.filter(models.Price.date <= end)
    return q.order_by(models.Price.date).all()
