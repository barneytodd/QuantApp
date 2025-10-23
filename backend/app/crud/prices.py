import threading
from datetime import date
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

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
def get_prices_light(db: Session, symbols, start, end, lookback):
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
def upsert_prices(db: Session, price_list: list[PriceIn], chunk_size: int = 5000):
    """
    Efficient, atomic bulk upsert into dbo.prices using SQL Server MERGE.

    - Uses a single raw connection and transaction.
    - Creates a temporary table once, inserts all batches.
    - Performs one MERGE at the end for consistency.
    - Safe for multi-threaded use (thread-local temp table name).
    """
    if not price_list:
        return

    # Get raw connection from SQLAlchemy engine � stays consistent for transaction
    engine: Engine = db.get_bind()
    with engine.begin() as connection:  # ensures commit/rollback automatically
        raw_conn = connection.connection
        cursor = raw_conn.cursor()

        temp_table = f"#TempPrices_{threading.get_ident()}"

        # Recreate temp table only once
        cursor.execute(f"""
            IF OBJECT_ID('tempdb..{temp_table}') IS NOT NULL DROP TABLE {temp_table};
            CREATE TABLE {temp_table} (
                symbol NVARCHAR(32) NOT NULL,
                [date] DATE NOT NULL,
                [open] FLOAT,
                [high] FLOAT,
                [low] FLOAT,
                [close] FLOAT,
                volume INT
            );
        """)

        # Enable fast executemany for performance
        cursor.fast_executemany = True
        insert_sql = f"""
            INSERT INTO {temp_table} (symbol, [date], [open], [high], [low], [close], volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        # Insert in chunks
        for i in range(0, len(price_list), chunk_size):
            batch = price_list[i:i + chunk_size]
            rows = [
                (p.symbol, p.date, p.open, p.high, p.low, p.close, p.volume)
                for p in batch
            ]
            cursor.executemany(insert_sql, rows)

        # Perform one MERGE operation
        merge_sql = f"""
            MERGE dbo.prices AS target
            USING {temp_table} AS source
                ON target.symbol = source.symbol AND target.[date] = source.[date]
            WHEN MATCHED THEN
                UPDATE SET
                    target.[open] = source.[open],
                    target.[high] = source.[high],
                    target.[low] = source.[low],
                    target.[close] = source.[close],
                    target.volume = source.volume
            WHEN NOT MATCHED THEN
                INSERT ([symbol], [date], [open], [high], [low], [close], [volume])
                VALUES (source.symbol, source.[date], source.[open],
                        source.[high], source.[low], source.[close], source.volume);
        """
        cursor.execute(merge_sql)
        # commit handled by `with engine.begin()`
        cursor.close()