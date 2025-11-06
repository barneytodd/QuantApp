import threading
import time
import uuid
from datetime import date
from typing import List, Optional

import pyodbc
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
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
def get_prices_light(db, symbols, start, end, lookback=0):
    """
    Fetch OHLC price data for multiple symbols efficiently without IN clause
    and with optional lookback, using window functions.
    
    Args:
        db (Session): SQLAlchemy session
        symbols (list[str]): list of symbols
        start (date/datetime): start date
        end (date/datetime): end date
        lookback (int): optional number of trading days to include before start
    
    Returns:
        pd.DataFrame: columns=['symbol', 'date', 'close', 'high', 'low']
    """
    if not symbols:
        return None

    # --- Use temp table approach to avoid IN ---
    # 1. Create a table variable with symbols
    symbols_table = ", ".join(f"('{s}')" for s in symbols)
    sql = f"""
    WITH symbol_list(symbol) AS (
        SELECT * FROM (VALUES {symbols_table}) AS t(symbol)
    ),
    ranked AS (
        SELECT p.symbol, p.[date], p.[close], p.[high], p.[low],
               ROW_NUMBER() OVER(PARTITION BY p.symbol ORDER BY p.[date]) AS rn
        FROM dbo.prices p
        JOIN symbol_list s ON s.symbol = p.symbol
        WHERE p.[date] <= :end
    )
    SELECT symbol, [date], [close], [high], [low]
    FROM ranked
    WHERE [date] >= DATEADD(DAY, -:lookback, :start) -- lookback applied
      AND [date] <= :end
    ORDER BY symbol, [date]
    """

    params = {"start": start, "end": end, "lookback": lookback}
    conn = db.connection()
    result = conn.execution_options(stream_results=True).execute(text(sql), params)

    for row in result:
        yield {
            "symbol": row.symbol,
            "date": row.date,
            "close": row.close,
            "high": row.high,
            "low": row.low,
        }


# === Upsert prices in bulk ===
def upsert_prices(db: Session, symbol: str, price_list: list, start, end, chunk_size: int = 500):
    """
    Efficient, atomic bulk upsert into dbo.prices using SQL Server MERGE.
    Handles duplicate (symbol, date) entries gracefully.
    """
    if not price_list:
        return

    engine: Engine = db.get_bind()

    with engine.begin() as connection:
        raw_conn = connection.connection
        cursor = raw_conn.cursor()

        temp_table = f"#TempPrices_{uuid.uuid4().hex}"

        # Drop existing temp table
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

        cursor.fast_executemany = True
        insert_sql = f"""
            INSERT INTO {temp_table} (symbol, [date], [open], [high], [low], [close], volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        MAX_INT = 2_147_483_647
        MIN_INT = -2_147_483_648


        for i in range(0, len(price_list), chunk_size):
            batch = price_list[i:i + chunk_size]
            valid_rows = []

            for j, p in enumerate(batch):
                skip_row = False

                # Check numeric limits
                for col_name, val in [
                    ("open", p.open),
                    ("high", p.high),
                    ("low", p.low),
                    ("close", p.close)
                ]:
                    if val is not None:
                        if not isinstance(val, (int, float)):
                            print(f"Row {i} invalid type in {col_name}: {val}")
                            skip_row = True
                            break
                        if abs(val) > 1e308:  # SQL Server FLOAT limit
                            print(f"Row {i} {col_name} too large: {val}")
                            skip_row = True
                            break

                # Check volume explicitly
                vol = p.volume
                if vol is not None:
                    if not isinstance(vol, int):
                        print(f"Row {i} volume invalid type: {vol}")
                        skip_row = True
                    elif vol < MIN_INT or vol > MAX_INT:
                        print(f"Row {i} volume out of range: {vol}")
                        skip_row = True

                if not skip_row:
                    valid_rows.append(
                        (p.symbol, p.date, p.open, p.high, p.low, p.close, p.volume)
                    )
                else:
                    print(f"Skipping row {i} for symbol {p.symbol} on date {p.date} with values {p}")

            if valid_rows:
                cursor.executemany(insert_sql, valid_rows)

        # Deduplicate and merge inline in one batch
        merge_sql = f"""
            ;WITH Deduped AS (
                SELECT *
                FROM (
                    SELECT *,
                           ROW_NUMBER() OVER(PARTITION BY symbol, [date] ORDER BY [date] DESC) AS rn
                    FROM {temp_table}
                ) t
                WHERE rn = 1
            )
            MERGE dbo.prices WITH (HOLDLOCK) AS target
            USING Deduped AS source
                ON target.symbol = source.symbol AND target.[date] = source.[date]
            WHEN MATCHED THEN
                UPDATE SET
                    target.[open]  = source.[open],
                    target.[high]  = source.[high],
                    target.[low]   = source.[low],
                    target.[close] = source.[close],
                    target.volume  = source.volume
            WHEN NOT MATCHED THEN
                INSERT ([symbol], [date], [open], [high], [low], [close], [volume])
                VALUES (source.symbol, source.[date], source.[open],
                        source.[high], source.[low], source.[close], source.volume);
        """
        cursor.execute(merge_sql)
        
        # Cleanup
        cursor.execute(f"DROP TABLE {temp_table};")
        cursor.close()


def upsert_prices_with_retry(db, symbol, price_list, start, end, chunk_size=500, retries=5, delay=2):
    for attempt in range(retries):
        try:
            upsert_prices(db, symbol, price_list, start, end, chunk_size)
            symbol_count = sum(1 for _ in price_list)
            db_records = get_prices_light(db, [symbol], start, end)
            db_count = sum(1 for _ in db_records)
            if db_count < symbol_count:
                print(f"Discrepancy for {symbol}: Fetched {symbol_count}, In DB {db_count}, retrying {attempt+1}/{retries}...")
                time.sleep(delay)
                continue
            break
        except (pyodbc.Error, OperationalError) as e:
            if "1205" in str(e):  # Deadlock victim
                if attempt < retries - 1:
                    print(f"Deadlock detected, retrying {attempt+1}/{retries}...")
                    time.sleep(delay)
                    continue
            raise  # re-raise if not a deadlock or out of retries