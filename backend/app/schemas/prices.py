from pydantic import BaseModel
from datetime import date
from typing import Union, List, Optional

# Input model for historical price data
class PriceIn(BaseModel):
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

# Output model for historical price data with ORM mode enabled
class PriceOut(PriceIn):
    id: int

    class Config:
        orm_mode = True

# Input model for symbol payloads
class SymbolPayload(BaseModel):
    symbols: Union[str, List[str]]
    period: Optional[str] = "1y"
    start: Optional[date] = None
    end: Optional[date] = None

class GetDataPayload(BaseModel):
    symbols: List[str]
    start: Optional[str] = None
    end: Optional[str] = None
