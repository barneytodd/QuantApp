from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Portfolio
from app.schemas import PortfolioOut, SavePortfolioPayload

router = APIRouter()


# === Save an optimised portfolio ===
@router.post("/save")
async def save_portfolio(payload: SavePortfolioPayload, db: Session = Depends(get_db)):
    """
    Save an optimised portfolio to the database.

    Args:
        payload: SavePortfolioPayload containing portfolio data and metadata
        db: SQLAlchemy session (dependency)

    Returns:
        dict: {"status": "success", "portfolio_id": <id>}
    
    Raises:
        HTTPException: If saving fails
    """
    try:
        ts = payload.timestamp or datetime.utcnow()
        new_portfolio = Portfolio(
            data=payload.portfolio,
            meta=payload.metadata,
            created_at=ts
        )
        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)

        return {"status": "success", "portfolio_id": new_portfolio.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save portfolio: {e}")


# === List all saved portfolios ===
@router.get("/list", response_model=List[PortfolioOut])
def list_portfolios(db: Session = Depends(get_db)):
    """
    Retrieve all saved portfolios, ordered by creation date descending.

    Args:
        db: SQLAlchemy session (dependency)

    Returns:
        List[PortfolioOut]: List of saved portfolios
    """
    portfolios = db.query(Portfolio).order_by(Portfolio.created_at.desc()).all()
    return portfolios
