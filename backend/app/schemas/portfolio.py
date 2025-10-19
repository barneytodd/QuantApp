from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

class PreScreenPayload(BaseModel):
    symbols: List[str]                      
    start: date
    end: date
    filters: Dict[str, Any]

class PortfolioInputsPayload(BaseModel):
    returns: Dict[str, List[float]]  # {"AAPL": [...], "MSFT": [...], ...}
    ewma_decay: float = 0.94

class HrpPayload(BaseModel):
    riskMatrix: Dict[str, Any]  # {"symbols": [...], "cov_matrix": [[...], [...], ...]})


class OptimisePayload(BaseModel):
    expected_returns: dict  # {"AAPL": 0.01, "MSFT": 0.008, ...}
    risk_matrix: dict       # {"symbols": [...], "cov_matrix": [[...], [...], ...]}
    baseline_weights: dict  # {"AAPL": 0.3, "MSFT": 0.25, ...}
    params: Dict[str, Any] = {}  # Additional parameters like risk_aversion, baseline_reg, max_weight