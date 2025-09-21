from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import SymbolPayload, PriceOut, PriceIn
from app.database import get_db
from app.services import fetcher
from app import crud

router = APIRouter()

# Get historical OHLCV data for a symbol
@router.get("/ohlcv/{symbol}", response_model=List[PriceOut])
def get_prices(symbol: str, start: str = None, end: str = None, db: Session = Depends(get_db)):
    rows = crud.get_prices(db, symbol, start, end)
    return rows

# Ingest historical OHLCV data for given symbols and period
@router.post("/ohlcv/")
def ingest_symbols(payload: SymbolPayload, background: BackgroundTasks, db: Session = Depends(get_db)):
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
