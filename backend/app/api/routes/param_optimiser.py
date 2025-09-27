from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ParamOptimisationRequest
from app.services.backtesting.engines.param_optimiser import optimise_parameters
from app.database import get_db
import numpy as np 
import datetime
from datetime import date
from app.utils.data_helpers import fetch_price_data

router = APIRouter()

@router.post("/optimise")
def analyze_and_select(payload: ParamOptimisationRequest, db: Session = Depends(get_db)):
	if not payload.symbols:
		raise HTTPException(status_code=400, detail="No symbols provided")

	if not payload.params:
		raise HTTPException(status_code=400, detail="No parameters provided")

	if not payload.optimParams:
		raise HTTPException(status_code=400, detail="No optimisation parameters provided")

	individual_symbols = [s[i] for s in payload.symbols for i in range(len(s))] 
	strategy_symbols = {"-".join(s):payload.strategy for s in payload.symbols}

	end_date = date.fromisoformat(payload.params["startDate"]["value"]) - datetime.timedelta(days=1)
	data = fetch_price_data(db, individual_symbols, end=payload.params["endDate"]["value"])

	return optimise_parameters(data, strategy_symbols, payload.params, payload.optimParams)