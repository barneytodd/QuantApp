from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import get_all_symbols
from app.database import get_db
from app.schemas import SymbolsRequest
from app.services.data import fetch_symbols

router = APIRouter()


# === Retrieve all symbols from the database ===
@router.get("/db_symbols")
def get_symbols(db: Session = Depends(get_db)):
    """
    Fetch all symbols currently stored in the database.

    Args:
        db: SQLAlchemy database session (injected via Depends).

    Returns:
        List of symbols.
    """
    return get_all_symbols(db)


# === Fetch available symbols from external source ===
@router.post("/fetch_symbols")
def get_available_symbols(payload: SymbolsRequest):
    """
    Retrieve symbols from an external source (e.g., Yahoo Finance) based on filters.

    Args:
        payload: SymbolsRequest containing optional filtering criteria:
            - filters: dictionary of filtering conditions (regions, exchanges, sectors, etc.)

    Returns:
        List of symbols matching the filter criteria.

    Raises:
        HTTPException: If no symbols are found.
    """
    filters = payload.filters or {}

    symbols = fetch_symbols.fetch_symbols(**filters)
    if not symbols:
        raise HTTPException(status_code=404, detail="No symbols found")
    
    return symbols
