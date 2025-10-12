from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import StrategyRequest
from app.services.backtesting.engines.backtest_engine import run_backtest
from app.database import get_db
from app.utils.data_helpers import fetch_price_data
from datetime import datetime, timedelta

router = APIRouter()

# enpoint to run backtest
@router.post("/backtest")
def run_strategy_backtest(payload: StrategyRequest, db: Session = Depends(get_db)):
    """
    Run a multi-strategy backtest on one or more symbols.

    This endpoint accepts a list of strategy configurations for various symbols,
    including both single-asset and pair strategies. Each (symbol, strategy) 
    combination is treated independently within the backtesting engine.

    Args:
        payload (StrategyRequest):
            The incoming request payload containing:
                - symbolItems: list of dicts, each with:
                    {
                        "symbols": [symbol1, symbol2?],
                        "strategy": strategy_name,
                        "weight": float
                    }
                - params: dict of strategy and backtest parameters
        db (Session):
            Active SQLAlchemy database session (dependency-injected).

    Behavior:
        - Builds a unique identifier for each (symbol, strategy) combo.
        - Fetches all required historical price data from the database.
        - Passes structured inputs into the `run_backtest` engine.
        - Supports multiple strategies per symbol (e.g. AAPL_momentum, AAPL_sma_crossover).
        - Handles both single-asset and pair-trading strategies.

    Returns:
        List[dict]:
            A list of backtest results, where each entry includes:
                - symbol (or pair identifier)
                - initial and final capital
                - performance metrics (e.g., Sharpe, drawdown)
                - equity curve data
                - trade logs and statistics

    Raises:
        HTTPException:
            - 400 if symbols or parameters are missing.
            - 404 if no price data is available for the given inputs.
    """

    if not payload.symbolItems:
        raise HTTPException(status_code=400, detail="No symbols provided")

    if not payload.params:
        raise HTTPException(status_code=400, detail="No parameters provided")

    # --- Collect all symbols (flat list) ---
    individual_symbols = list({s for item in payload.symbolItems for s in item["symbols"]})

    # --- Build symbol-strategy mapping ---
    strategy_symbols = {}
    for item in payload.symbolItems:
        key_base = "-".join(item["symbols"])
        strategy = item["strategy"]
        key = f"{key_base}_{strategy}"  # Unique key per symbol-strategy pair

        strategy_symbols[key] = {
            "symbol": key_base,   # e.g. "AAPL" or "AAPL-MSFT"
            "strategy": strategy,
            "weight": item.get("weight", 1),
        }

    # --- Compute lookback window ---
    max_lookback = max(
        (v["value"] for k, v in payload.params.items() if v.get("lookback")), default=0
    )

    # --- Fetch price data ---
    data = fetch_price_data(
        db,
        individual_symbols,
        payload.params["startDate"]["value"],
        payload.params["endDate"]["value"],
        max_lookback,
    )

    params = {p: v["value"] for p, v in payload.params.items()}

    # --- Run the backtest ---
    results = run_backtest(data, strategy_symbols, params, max_lookback)

    if not results:
        raise HTTPException(status_code=404, detail="No price data for given symbols")

    return results
