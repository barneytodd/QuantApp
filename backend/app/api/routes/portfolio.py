from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import PreScreenPayload
from app.database import get_db
from app import crud
from collections import defaultdict
from app.services.portfolio.stages.prescreen.run_prescreen import run_tests


router = APIRouter()

@router.post("/runPreScreen/")
def run_prescreen_tests(payload: PreScreenPayload, db: Session = Depends(get_db)):
    #payload has symbols, start, end, filters
    rows = crud.get_prices(db, payload.symbols, payload.start, payload.end)
    
    grouped_data = defaultdict(list)
    for row in rows:
        grouped_data[row.symbol].append({"date": row.date, "close": row.close, "high": row.high, "low": row.low})
    
    results = run_tests(grouped_data, payload.filters)
    return results