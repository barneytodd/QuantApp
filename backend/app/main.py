from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    backtest, pairs, param_optimiser,
    data, symbols, metrics, 
    portfolio_weights, save_portfolio, prescreen
)
from app.models import Base
from app.database import SessionLocal, engine, init_db_pool, close_db_pool


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


