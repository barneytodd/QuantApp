from datetime import date
from typing import Union, List, Optional
from pydantic import BaseModel, field_validator

# Input model for historical OHLCV data
class PriceIn(BaseModel):
    symbol: str  # Stock symbol
    date: date   # Date of the price record
    open: float
    high: float
    low: float
    close: float
    volume: int  # Trading volume

# Output model including database ID, using ORM mode
class PriceOut(PriceIn):
    id: int

    model_config = {
        "from_attributes": True  # Enable reading from ORM objects
    }

# Payload for symbol-based data ingestion or fetching
class SymbolPayload(BaseModel):
    symbols: Union[str, List[str]]  # Accept either a single symbol or a list
    period: Optional[str] = "1y"    # Default period if start/end not provided
    start: Optional[date] = None
    end: Optional[date] = None

    # Normalize single string input to a list
    @field_validator("symbols", mode="before")
    def normalize_symbols(cls, v):
        if isinstance(v, str):
            return [v]
        return v

# Payload for fetching historical price data for multiple symbols
class GetDataPayload(BaseModel):
    symbols: List[str]               # Must be a list of symbols
    start: Optional[date] = None     # Optional start date
    end: Optional[date] = None       # Optional end date
