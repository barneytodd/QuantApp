from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class PairSelectionRequest(BaseModel):
    # List of symbols to select pairs from
    symbols: List[str] = Field(
        ...,  # required field
        description="List of symbols to select pairs from (at least 2 required)"
    )

    # Optional start date
    start: Optional[date] = None

    # Optional end date
    end: Optional[date] = None
    
    # Weight for correlation in pair selection
    w_corr: float = Field(
        0.5,  # default value
        description="Weight for correlation in pair selection (0-1)"
    )
    
    # Weight for cointegration in pair selection
    w_coint: float = Field(
        0.5,  # default value
        description="Weight for cointegration in pair selection (0-1)"
    )

    # --- Validators ---

    # Ensure the symbols list contains at least 2 items
    @field_validator("symbols")
    def check_min_symbols(cls, v: List[str]) -> List[str]:
        if len(v) < 2:
            raise ValueError("At least 2 symbols are required")
        return v

    # Ensure w_corr and w_coint are within [0, 1]
    @field_validator("w_corr", "w_coint")
    def check_weight_range(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("Weight must be between 0 and 1")
        return v

    # --- Extra JSON schema for documentation / examples ---
    model_config = {
        "json_schema_extra": {
            "example": {
                "symbols": ["AAPL", "MSFT", "GOOG"],
                "w_corr": 0.6,
                "w_coint": 0.4
            }
        }
    }
