from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import PairSelectionRequest
from app.utils.pair_selection import select_pairs_max_weight
from app.services.backtesting.engines.pairs_selection import analyze_pairs
from app.crud import get_prices as crud_get_prices
from app.database import get_db
import numpy as np 

router = APIRouter()

@router.post("/select")
def analyze_and_select(req: PairSelectionRequest, db: Session = Depends(get_db)):
    
    prices_dict = {}
    for sym in req.symbols:
        rows = crud_get_prices(db, sym)
        if not rows:
            continue
        prices_dict[sym] = [{"date": r.date, "close": r.close} for r in rows]

    if len(prices_dict) < 2:
        raise HTTPException(status_code=404, detail="Not enough price data for selected symbols")

    pairs = analyze_pairs(req.symbols, prices_dict, req.w_corr, req.w_coint)
    selected = select_pairs_max_weight(pairs, weight_key="score")
    return {
        "all_pairs": pairs,
        "selected_pairs": selected
    }
