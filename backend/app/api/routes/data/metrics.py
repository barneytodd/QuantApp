import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import get_prices
from app.database import get_db
from app.schemas import StatsOut

router = APIRouter()


# === Calculate financial metrics for a symbol ===
@router.get("/{symbol}", response_model=StatsOut)
def get_metrics(symbol: str, start: str = None, end: str = None, db: Session = Depends(get_db)):
    """
    Retrieve historical price data for a symbol and compute key financial metrics.

    Args:
        symbol: Ticker symbol to calculate metrics for.
        start: Optional start date (YYYY-MM-DD).
        end: Optional end date (YYYY-MM-DD).

    Returns:
        Dictionary containing:
            - symbol
            - start_date
            - end_date
            - annualised_volatility
            - mean_return
            - sharpe_ratio
            - max_drawdown

    Raises:
        HTTPException: If no price data is found.
    """
    # Fetch OHLCV close prices from the database
    rows = get_prices(db, [symbol], start, end)
    if not rows:
        raise HTTPException(status_code=404, detail="No price data")

    # Convert to DataFrame
    df = pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])
    df = df.set_index("date").sort_index()

    # Calculate daily returns
    df["returns"] = df["close"].pct_change().dropna()

    # Annualisation factor (daily data)
    ann_factor = 252

    # Key metrics
    vol = df["returns"].std() * (ann_factor**0.5)        # Annualised volatility
    mean_ret = df["returns"].mean() * ann_factor         # Annualised mean return
    sharpe = mean_ret / vol if vol > 0 else None        # Sharpe ratio
    cummax = df["close"].cummax()                       # Running max for drawdown
    drawdown = (df["close"] - cummax) / cummax          # Drawdown series
    max_dd = drawdown.min()                              # Maximum drawdown

    return {
        "symbol": symbol,
        "start_date": df.index.min(),
        "end_date": df.index.max(),
        "annualised_volatility": float(vol),
        "mean_return": float(mean_ret),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(max_dd)
    }
