# Main FastAPI application for Q-PATS Phase 1

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.models import Price, Base
from app.schemas import PriceIn, PriceOut, SymbolPayload, StatsOut
from app.crud import get_prices, upsert_prices, get_all_symbols
from .database import SessionLocal, engine
from .database_async import init_db_pool, close_db_pool
from .services.data import fetcher
import pandas as pd
from datetime import date
from typing import List
from app.api.routes import data, metrics, backtest, symbols, pairs, param_optimiser, prescreen, portfolio_weights, save_portfolio


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Trading Strategy API",
    description="API for running trading strategy backtests",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",  # frontend dev server
    "http://127.0.0.1:3000"
]



# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(backtest.router, prefix="/api/strategies", tags=["Backtest"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(symbols.router, prefix="/api/symbols", tags=["Data"])
app.include_router(pairs.router, prefix="/api/pairs", tags=["Pairs"])
app.include_router(param_optimiser.router, prefix="/api/params", tags=["Backtest"])
app.include_router(prescreen.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(portfolio_weights.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(save_portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])

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

@app.on_event("startup")
async def on_startup():
    await init_db_pool()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db_pool()


