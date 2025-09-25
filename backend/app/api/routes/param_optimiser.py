from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ParamOptimisationRequest
from app.services.backtesting.param_optimiser import optimise_parameters
from app.database import get_db
import numpy as np 

router = APIRouter()

@router.post("/optimise")
def analyze_and_select(req: ParamOptimisationRequest, db: Session = Depends(get_db)):
	return optimise_parameters(req.strategy, req.symbols, req.params, req.optimParams, db)