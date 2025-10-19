from fastapi import APIRouter, HTTPException, Depends  
from app.schemas import SavePortfolioPayload, PortfolioOut
from typing import List
from datetime import datetime
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import Portfolio


router = APIRouter()

@router.post("/save")
async def save_portfolio(payload: SavePortfolioPayload, db: Session = Depends(get_db)):
    """
    Save an optimised portfolio to the database.
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


@router.get("/list", response_model=List[PortfolioOut])
def list_portfolios(db: Session = Depends(get_db)):
    """
    Load all saved portfolios from the database.
    """
    portfolios = db.query(Portfolio).order_by(Portfolio.created_at.desc()).all()
    return portfolios