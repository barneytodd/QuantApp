from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import StrategyRequest
from app.services.backtesting.engines.backtest_engine import run_backtest
from app.database import get_db
from app.utils.data_helpers import fetch_price_data

router = APIRouter()

# enpoint to run backtest
@router.post("/backtest")
def run_strategy_backtest(payload: StrategyRequest, db: Session = Depends(get_db)):
    if not payload.symbolItems:
        raise HTTPException(status_code=400, detail="No symbols provided")

    if not payload.params:
        raise HTTPException(status_code=400, detail="No parameters provided")

    individual_symbols = [s["symbols"][i] for s in payload.symbolItems for i in range(len(s["symbols"]))] 
    strategy_symbols = {"-".join(s["symbols"]):s["strategy"] for s in payload.symbolItems}
    data = fetch_price_data(db, individual_symbols, payload.params["startDate"], payload.params["endDate"])
    results = run_backtest(data, strategy_symbols, payload.params)

    if not results:
        raise HTTPException(status_code=404, detail="No price data for given symbols")

    return results
