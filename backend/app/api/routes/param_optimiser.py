from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ParamOptimisationRequest
from app.utils.pair_selection import select_pairs_max_weight
from app.services.backtesting.pairs_service import analyze_pairs
from app.crud import get_prices as crud_get_prices
from app.database import get_db
import numpy as np 

router = APIRouter()

@router.post("/optimise")
def analyze_and_select(req: ParamOptimisationRequest, db: Session = Depends(get_db)):
	print("optimising parameters ... ")
	return True