from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import get_all_symbols
from app.database import get_db
from app.services.data import fetcher

router = APIRouter()

# Get all symbols stored in the database
@router.get("/db_symbols")
def get_symbols(db: Session = Depends(get_db)):
    return get_all_symbols(db)

# Fetch available symbols from external data source
@router.get("/fetch_symbols")
def get_available_symbols():
    symbols = fetcher.fetch_symbols()
    if not symbols:
        raise HTTPException(status_code=404, detail="No symbols found")
    return symbols
