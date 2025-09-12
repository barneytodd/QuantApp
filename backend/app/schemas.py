#Define Pydantic models for request and response schemas

from pydantic import BaseModel
from datetime import date
from typing import List

# Defines data structure for incoming price records
class PriceIn(BaseModel):
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

# Defines data structure for fetched price records (inherits all fields from PriceIn))
class PriceOut(PriceIn):
    id: int
    class Config:
        orm_mode = True

# Defines data structure for calculated statistics for a symbol
class StatsOut(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    annualised_volatility: float
    mean_return: float
    sharpe_ratio: float
    max_drawdown: float
