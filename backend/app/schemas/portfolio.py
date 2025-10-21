from datetime import datetime, date
from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class PreScreenPayload(BaseModel):
    symbols: List[str]                      
    start: date
    end: date
    filters: Dict[str, Any]

class PortfolioInputsPayload(BaseModel):
    returns: Dict[str, Any]  # {"AAPL": [...], "MSFT": [...], ...}
    ewma_decay: float = 0.94

class HrpPayload(BaseModel):
    riskMatrix: Dict[str, Any]  # {"symbols": [...], "cov_matrix": [[...], [...], ...]})


class OptimisePayload(BaseModel):
    expected_returns: dict  # {"AAPL": 0.01, "MSFT": 0.008, ...}
    risk_matrix: dict       # {"symbols": [...], "cov_matrix": [[...], [...], ...]}
    baseline_weights: dict  # {"AAPL": 0.3, "MSFT": 0.25, ...}
    params: Dict[str, Any] = {}  # Additional parameters like risk_aversion, baseline_reg, max_weight

class SavePortfolioPayload(BaseModel):
    portfolio: Dict[str, Any]  # {"sma_crossover": {"symbolsWithWeights": [{"symbol": "AAPL", "weight": 0.3}, ...], "params": {"shortPeriod": 20, ...}}, ...}
    metadata: Optional[Dict[str, Any]] = {}
    timestamp: Optional[datetime] = None


class PortfolioOut(BaseModel):
    id: int
    data: dict
    meta: Optional[dict] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }