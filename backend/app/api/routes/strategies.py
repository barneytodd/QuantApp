from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import StrategyRequest
from app.services.backtesting.engines import backtest_engine, pairs_backtest_engine
from app.database import get_db
from app.crud import get_prices as crud_get_prices
from app.strategies.strategy_registry import strategies
from app.utils.pairs_helpers import align_series
from app.utils.data_helpers import fetch_price_data

router = APIRouter()

# enpoint to run backtest
@router.post("/backtest")
def run_strategy_backtest(payload: StrategyRequest, db: Session = Depends(get_db)):
    if not payload.symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")

    if not payload.params:
        raise HTTPException(status_code=400, detail="No parameters provided")

    individual_results = []

    if payload.strategy == "pairs_trading":
        for pair in payload.pairs:
            symbol1, symbol2 = pair["stock1"], pair["stock2"]

            price_dict = {}
            for symbol in [symbol1, symbol2]:
                individual_data = fetch_price_data(db, symbol, payload.params["startDate"], payload.params["endDate"])

                price_dict[symbol] = individual_data
            
            data = align_series(price_dict, symbol1, symbol2)

            result = strategies[payload.strategy](
            data=data,
            params=payload.params,
            stock1 = symbol1,
            stock2 = symbol2,
            initial_capital=payload.params["initialCapital"] / len(payload.pairs) 
            )


            individual_results.append(result)

        if not individual_results:
            raise HTTPException(status_code=404, detail="No price data for given symbols")

        # Combine all results
        combined_result = pairs_backtest_engine.combine_pairs_results(individual_results)
        individual_results.append(combined_result)

    else:
        for symbol in payload.symbols:
        
            # Fetch OHLCV data from DB
            data = fetch_price_data(db, symbol, payload.params["startDate"], payload.params["endDate"])
        
            # Run the backtest
            result = strategies[payload.strategy](
                data=data,
                params=payload.params,
                initial_capital=payload.params["initialCapital"] / len(payload.symbols)
            )


            individual_results.append(result)

        if not individual_results:
            raise HTTPException(status_code=404, detail="No price data for given symbols")
    
        # Combine all results
        combined_result = backtest_engine.combine_results(individual_results)
        individual_results.append(combined_result)

    return individual_results
