from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from app.crud import get_prices
from app.database import get_db
from app.schemas import StatsOut

router = APIRouter()

# Calculate and return financial metrics for a given symbol and date range
@router.get("/{symbol}", response_model=StatsOut)
def get_metrics(symbol: str, start: str = None, end: str = None, db: Session = Depends(get_db)):
    rows = get_prices(db, [symbol], start, end)
    if not rows:
        raise HTTPException(status_code=404, detail="No price data")
    
    df = pd.DataFrame([{"date": r.date, "close": r.close} for r in rows]).set_index("date").sort_index()
    df["returns"] = df["close"].pct_change().dropna()
    ann_factor = 252
    vol = df["returns"].std() * (ann_factor**0.5)
    mean_ret = df["returns"].mean() * ann_factor
    sharpe = mean_ret / vol if vol > 0 else None
    cummax = df["close"].cummax()
    drawdown = (df["close"] - cummax) / cummax
    max_dd = drawdown.min()

    return {
        "symbol": symbol,
        "start_date": df.index.min(),
        "end_date": df.index.max(),
        "annualised_volatility": float(vol),
        "mean_return": float(mean_ret),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(max_dd)
    }
