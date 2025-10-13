from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import SymbolPayload, PriceOut, PriceIn, GetDataPayload
from app.database import get_db
from app.services.data import fetcher
from app import crud

router = APIRouter()

# Get historical OHLCV data for a symbol
@router.get("/ohlcv/{symbol}", response_model=List[PriceOut])
def get_prices(symbol: str, start: str = None, end: str = None, db: Session = Depends(get_db)):
    rows = crud.get_prices(db, [symbol], start, end)
    return rows

# Get historical OHLCV data for a list of symbols
@router.post("/ohlcv/", response_model=List[PriceOut])
def get_prices(payload: GetDataPayload, db: Session = Depends(get_db)):
    start = payload.start if payload.start else None
    end = payload.end if payload.end else None
    rows = crud.get_prices(db, payload.symbols, start, end)
    return rows

# Ingest historical OHLCV data for given symbols and period
@router.post("/ohlcv/ingest/")
def ingest_prices(payload: SymbolPayload, background: BackgroundTasks, db: Session = Depends(get_db)):
    symbols = payload.symbols
    if isinstance(symbols, str):
        symbols = [symbols]
    background.add_task(_ingest_task, symbols, payload.period, db)
    return {"status": "ingestion started", "symbols": symbols}

# Background task to fetch and store data
def _ingest_task(symbols: List[str], period: str, db: Session):
    records = fetcher.fetch_historical(symbols, period)
    if not records:
        raise HTTPException(status_code=404, detail="No data fetched")
    crud.upsert_prices(db, [PriceIn(**r) for r in records])

@router.post("/ohlcv/syncIngest/")
def ingest_prices_synchronously(payload: SymbolPayload, db: Session = Depends(get_db)):
    symbols = payload.symbols
    if isinstance(symbols, str):
        symbols = [symbols]

    # Fetch and insert immediately
    result = fetcher.ingest_missing_data_parallel(db, symbols, payload.start, payload.end)

    if result:
        print("Data ingestion complete")
        return {"status": "ingestion complete", "symbols": symbols}

    else:
        raise HTTPException(status_code=404, detail="No data fetched")
