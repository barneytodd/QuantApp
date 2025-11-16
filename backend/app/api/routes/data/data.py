from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import GetDataPayload, PriceIn, PriceOut, SymbolPayload
from app.services.data import fetch_prices

router = APIRouter()


# === Get historical OHLCV data for a single symbol ===
@router.get("/ohlcv/{symbol}", response_model=List[PriceOut])
def get_prices(symbol: str, start: str = None, end: str = None, db: Session = Depends(get_db)):
    """
    Retrieve historical OHLCV (Open, High, Low, Close, Volume) data for a single symbol.

    Args:
        symbol: Ticker symbol to fetch data for.
        start: Optional start date (YYYY-MM-DD).
        end: Optional end date (YYYY-MM-DD).

    Returns:
        List of PriceOut objects containing OHLCV data.
    """
    rows = crud.get_prices(db, [symbol], start, end)
    return rows


# === Get historical OHLCV data for multiple symbols ===
@router.post("/ohlcv/", response_model=List[PriceOut])
def get_prices(payload: GetDataPayload, db: Session = Depends(get_db)):
    """
    Retrieve OHLCV data for multiple symbols at once.

    Args:
        payload.symbols: List of ticker symbols.
        payload.start: Optional start date.
        payload.end: Optional end date.

    Returns:
        List of PriceOut objects containing OHLCV data.
    """
    start = payload.start or None
    end = payload.end or None
    rows = crud.get_prices(db, payload.symbols, start, end)
    return rows


# === Schedule background ingestion of OHLCV data ===
@router.post("/ohlcv/ingest/")
def ingest_prices(payload: SymbolPayload, background: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Schedule a background task to ingest OHLCV data for given symbols and period.

    Args:
        payload.symbols: Single symbol or list of symbols.
        payload.period: Period to fetch (e.g., '1y', '6mo', etc.)

    Returns:
        Status message and list of symbols being ingested.
    """
    symbols = payload.symbols
    if isinstance(symbols, str):
        symbols = [symbols]

    # Add ingestion task to FastAPI background tasks
    background.add_task(_ingest_task, symbols, payload.period, db)
    return {"status": "ingestion started", "symbols": symbols}


# === Background task helper ===
def _ingest_task(symbols: List[str], period: str, db: Session):
    """
    Background function to fetch OHLCV data and insert into database.

    Raises HTTPException if no data is fetched.
    """
    records = fetch_prices.fetch_historical(symbols, period, db=db)
    
    if not records:
        raise HTTPException(status_code=404, detail="No data fetched")
    
    all_records = {symbol: [] for symbol in symbols}
    for symbol in symbols: 
        crud.upsert_prices(db, symbol, [PriceIn(**r) for r in records if r["symbol"] == symbol])


# === Synchronous ingestion of missing OHLCV data ===
@router.post("/ohlcv/syncIngest/")
def ingest_prices_synchronously(payload: SymbolPayload, db: Session = Depends(get_db)):
    """
    Fetch missing OHLCV data immediately and insert into the database.

    Args:
        payload.symbols: Single symbol or list of symbols.
        payload.start: Start date of data range.
        payload.end: End date of data range.

    Returns:
        Status message and list of ingested symbols.

    Raises:
        HTTPException if no data is fetched.
    """
    symbols = payload.symbols
    if isinstance(symbols, str):
        symbols = [symbols]

    result = fetch_prices.ingest_missing_data_parallel(db, symbols, payload.start, payload.end)

    if result:
        return {"status": "ingestion complete", "symbols": symbols}

    raise HTTPException(status_code=404, detail="No data fetched")
