from datetime import date
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import text, tuple_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prices import Price
from app.schemas.prices import PriceIn


# Get historical OHLCV data for a symbol, optionally filtered by date range
def get_prices(symbols: List[str], start: Optional[date] = None, end: Optional[date] = None, lookback: Optional[int] = 0, db: Session = Depends(get_db)) -> List[Price]:
    query = db.query(Price).filter(Price.symbol.in_(symbols))

    if start and lookback and lookback > 0:
        # Find the cutoff date by looking back N trading days
        subquery = (
            db.query(Price.date)
            .filter(Price.symbol.in_(symbols), Price.date <= start)
            .order_by(Price.date.desc())
            .limit(lookback)
            .subquery()
        )
        cutoff_date = db.query(subquery.c.date).order_by(subquery.c.date.asc()).first()
        if cutoff_date:
            start = cutoff_date[0]

    if start:
        query = query.filter(Price.date >= start)
    if end:
        query = query.filter(Price.date <= end)
    return query.order_by(Price.date.asc()).all()


def get_prices_light(db, symbols, start, end, lookback):
    if not symbols:
        return []
    
    if start and lookback and lookback > 0:
        # Find the cutoff date by looking back N trading days
        subquery = (
            db.query(Price.date)
            .filter(Price.symbol.in_(symbols), Price.date <= start)
            .order_by(Price.date.desc())
            .limit(lookback)
            .subquery()
        )
        cutoff_date = db.query(subquery.c.date).order_by(subquery.c.date.asc()).first()
        if cutoff_date:
            start = cutoff_date[0]

    # Build parameter placeholders dynamically
    placeholders = ", ".join([f":s{i}" for i in range(len(symbols))])
    params = {f"s{i}": sym for i, sym in enumerate(symbols)}
    params.update({"start": start, "end": end})

    sql = text(f"""
        SELECT symbol, [date], [close], [high], [low]
        FROM dbo.prices WITH (NOLOCK)
        WHERE symbol IN ({placeholders})
          AND [date] BETWEEN :start AND :end
        ORDER BY symbol, [date];
    """)

    result = db.execute(sql, params)

    return [
        {
            "symbol": r.symbol,
            "date": r.date,
            "close": r.close,
            "high": r.high,
            "low": r.low,
        }
        for r in result
    ]



# Upsert a list of PriceIn records into the database
def upsert_prices(db: Session, price_list: List[PriceIn], chunk_size: int = 500):
    """
    Efficient bulk upsert for a list of PriceIn objects into the Price table.

    Args:
        db: SQLAlchemy Session
        price_list: List of PriceIn objects
        chunk_size: Number of rows to process per internal batch
    """
    # Process in manageable batches to avoid memory / query overload
    for i in range(0, len(price_list), chunk_size):
        batch = price_list[i:i + chunk_size]

        # 1 Collect all (symbol, date) keys from the batch
        keys = [(p.symbol, p.date) for p in batch]

        # 2 Fetch existing rows in a single query
        existing_rows = db.query(Price).filter(
            tuple_(Price.symbol, Price.date).in_(keys)
        ).all()
        existing_dict = {(r.symbol, r.date): r for r in existing_rows}

        # 3 Prepare lists for updates and inserts
        to_insert = []

        for price in batch:
            key = (price.symbol, price.date)
            if key in existing_dict:
                # Update existing row in memory
                db_price = existing_dict[key]
                db_price.open = price.open
                db_price.high = price.high
                db_price.low = price.low
                db_price.close = price.close
                db_price.volume = price.volume
            else:
                # Collect new rows for bulk insert
                to_insert.append(Price(**price.dict()))

        # 4 Bulk insert new rows in one query
        if to_insert:
            db.bulk_save_objects(to_insert)

        # 5 Commit once per batch
        db.commit()
