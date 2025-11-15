from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api import (
    backtest, pairs, param_optimiser,
    data, symbols, metrics, 
    portfolio_weights, save_portfolio, prescreen
)
from app.data import portfolio_seed_data
from app.models import Base, Portfolio
from app.database import SessionLocal, engine, init_db_pool, close_db_pool

def seed_portfolios(db: Session):
    # Only seed if table is empty
    if db.query(Portfolio).count() == 0:
        for portfolio in portfolio_seed_data:
            db.add(Portfolio(**portfolio))
        db.commit()

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed portfolios on first creation
with SessionLocal() as db:
    seed_portfolios(db)

# Lifespan context manager replaces on_event startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB pool
    await init_db_pool()
    yield
    # Shutdown: close DB pool
    await close_db_pool()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Trading Strategy API",
    description="API for running trading strategy backtests and portfolio analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check
@app.get("/api/health")
def health():
    return {"status": "ok"}
