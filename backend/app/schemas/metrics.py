from datetime import date

from pydantic import BaseModel


# Response model for statistical metrics of a trading symbol
class StatsOut(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    annualised_volatility: float
    mean_return: float
    sharpe_ratio: float
    max_drawdown: float
