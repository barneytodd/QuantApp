# Main FastAPI application for Q-PATS Phase 1

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, crud
from .database import SessionLocal, engine
from .services import fetcher
import pandas as pd
from datetime import date

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Q-PATS Phase 1")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency - provides database sessions to endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/api/health")
def health():
    return {"status": "ok"}

# Get historical prices for a given symbol and optional date range
@app.get("/api/ohlcv/{symbol}", response_model=list[schemas.PriceOut])
def get_prices(symbol: str, start: date = None, end: date = None, db: Session = Depends(get_db)):
    rows = crud.get_prices(db, symbol, start, end)
    return rows

# Get statistics for a given symbol and optional date range
@app.get("/api/metrics/{symbol}", response_model=schemas.StatsOut)
def get_stats(symbol: str, start: date = None, end: date = None, db: Session = Depends(get_db)):
    rows = crud.get_prices(db, symbol, start, end)
    if not rows:
        raise HTTPException(status_code=404, detail="no price data")
    df = pd.DataFrame([{
        "date": r.date,
        "close": r.close
    } for r in rows]).set_index("date").sort_index()

    # Daily returns (% change in closing price from previous day))
    df["returns"] = df["close"].pct_change().dropna()

    # Annualization factor (252 trading days)
    ann_factor = 252

    # Annualized volatility
    vol = df["returns"].std() * (ann_factor**0.5)

    # Mean return
    mean_ret = df["returns"].mean() * ann_factor

    # Sharpe ratio 
    sharpe = mean_ret / vol if vol > 0 else None

    # Cummulative maximum of closing prices
    cummax = df["close"].cummax()

    # Drawdown series (percentage drop from peak)
    drawdown = (df["close"] - cummax) / cummax

    # Maximum drawdown (biggest peak-to-trough loss))
    max_dd = drawdown.min()

    return {
        "symbol": symbol,
        "start_date": df.index.min(),
        "end_date": df.index.max(),
        "annualised_volatility": float(vol),
        "mean_return": float(mean_ret),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(max_dd)
    }

# Get list of all symbols in the database
@app.get("/api/symbols")
def get_symbols(db: Session = Depends(get_db)):
    rows = db.query(models.Price.symbol).distinct().all()
    return [r[0] for r in rows]

# Ingest historical price data in the background
@app.post("/api/ohlcv/{symbol}")
def ingest_symbol(
    symbol: str,
    background: BackgroundTasks,
    period: str = "1y",
    db: Session = Depends(get_db)
):
    if background:
        background.add_task(_ingest_task, symbol, period, db)
        return {"status": "ingestion started"}
    else:
        return _ingest_task(symbol, period, db)


# Task to fetch and store historical data
def _ingest_task(symbol: str, period: str, db: Session):
    records = fetcher.fetch_historical(symbol, period=period)
    if not records:
        raise HTTPException(status_code=404, detail="No data fetched")
    crud.upsert_prices(db, [schemas.PriceIn(**r) for r in records])
    return {"symbol": symbol, "rows": len(records)}