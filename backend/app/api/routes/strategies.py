from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import StrategyRequest
from app.services import backtest_engine
from app.database import get_db
from app.crud import get_prices as crud_get_prices
from app.services.strategy_registry import strategies

router = APIRouter()

# enpoint to run backtest
@router.post("/backtest")
def run_strategy_backtest(payload: StrategyRequest, db: Session = Depends(get_db)):
    if not payload.symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")

    if not payload.params:
        raise HTTPException(status_code=400, detail="No parameters provided")


    individual_results = []

    for symbol in payload.symbols:
        
        # Fetch OHLCV data from DB
        data_rows = crud_get_prices(db, symbol)
        if not data_rows:
            continue

        # Convert SQLAlchemy objects to dict
        data = [
            {
                "date": r.date.isoformat(),
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "symbol": r.symbol
            } for r in data_rows
        ]
        
        # Run the backtest
        result = strategies[payload.strategy](
            data=data,
            params=payload.params,
            initial_capital=payload.initialCapital / len(payload.symbols)
        )


        individual_results.append(result)

    if not individual_results:
        raise HTTPException(status_code=404, detail="No price data for given symbols")
    
    # Combine all results
    combined_result = backtest_engine.combine_results(individual_results)
    individual_results.append(combined_result)

    return individual_results
