from datetime import date
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import text, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prices import Price
from app.schemas.data.prices import PriceIn


# === Get historical OHLCV data for one or more symbols ===
def get_prices(
    db: Session,
    symbols: List[str], 
    start: Optional[date] = None, 
    end: Optional[date] = None, 
    lookback: Optional[int] = 0
) -> List[Price]:
    """
    Retrieve historical OHLCV data for a list of symbols with optional date filtering
    and lookback functionality.

    Args:
        symbols: List of symbols to fetch
        start: Optional start date
        end: Optional end date
        lookback: Optional number of trading days to look back from start
        db: SQLAlchemy session

    Returns:
        List[Price]: List of Price ORM objects ordered by date ascending
    """
    query = db.query(Price).filter(Price.symbol.in_(symbols))

    if start and lookback and lookback > 0:
        # Adjust start date based on lookback
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


# === Lightweight price fetch using raw SQL ===
def get_prices_light(db, symbols, start, end, lookback):
    """
    Fetch price data for multiple symbols efficiently using raw SQL.
    Supports lookback for start date adjustment.

    Args:
        db: SQLAlchemy session
        symbols: List of symbols
        start: Start date
        end: End date
        lookback: Optional lookback window in trading days

    Returns:
        List[dict]: Each dict contains symbol, date, close, high, low
    """
    if not symbols:
        return []

    if start and lookback and lookback > 0:
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

    # Build parameterized query
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
        {"symbol": r.symbol, "date": r.date, "close": r.close, "high": r.high, "low": r.low}
        for r in result
    ]


# === Upsert prices in bulk ===
def upsert_prices(db: Session, price_list: List[PriceIn], chunk_size: int = 500):
    """
    Efficiently upsert a batch of PriceIn objects into the Price table.

    Args:
        db: SQLAlchemy session
        price_list: List of PriceIn objects
        chunk_size: Number of rows per batch commit
    """
    for i in range(0, len(price_list), chunk_size):
        batch = price_list[i:i + chunk_size]

        # Collect keys (symbol, date) for existing lookup
        keys = [(p.symbol, p.date) for p in batch]
        conditions = [((Price.symbol == sym) & (Price.date == dt)) for sym, dt in keys]
        
        existing_rows = db.query(Price).filter(or_(*conditions)).all()
        existing_dict = {(r.symbol, r.date): r for r in existing_rows}

        to_insert = []

        for price in batch:
            key = (price.symbol, price.date)
            if key in existing_dict:
                # Update existing row
                db_price = existing_dict[key]
                db_price.open = price.open
                db_price.high = price.high
                db_price.low = price.low
                db_price.close = price.close
                db_price.volume = price.volume
            else:
                # Collect for bulk insert
                to_insert.append(Price(**price.dict()))
        print(to_insert[:2])  # Debug: print first 2 inserts)
        if to_insert:
            db.bulk_save_objects(to_insert)

        db.commit()
