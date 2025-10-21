from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Payload for pre-screening multiple symbols over a date range with optional filters
class PreScreenPayload(BaseModel):
    symbols: List[str]                  # List of symbols to pre-screen
    start: date                         # Start date of the backtest/pre-screen period
    end: date                           # End date of the backtest/pre-screen period
    filters: Dict[str, Any]             # Optional filters to refine the pre-screening (e.g., strategy, sector)

# Payload to compute portfolio inputs such as expected returns and risk matrix
class PortfolioInputsPayload(BaseModel):
    returns: Dict[str, Any]             # Historical returns per symbol, e.g., {"AAPL": [...], "MSFT": [...]}
    ewma_decay: float = 0.94            # EWMA decay factor for risk calculations

# Payload for computing Hierarchical Risk Parity (HRP) allocation
class HrpPayload(BaseModel):
    riskMatrix: Dict[str, Any]          # Covariance matrix and symbols, e.g., {"symbols": [...], "cov_matrix": [[...], ...]}

# Payload to optimise portfolio weights
class OptimisePayload(BaseModel):
    expected_returns: dict              # Expected returns per symbol, e.g., {"AAPL": 0.01, "MSFT": 0.008}
    risk_matrix: dict                   # Covariance/risk matrix, e.g., {"symbols": [...], "cov_matrix": [[...], ...]}
    baseline_weights: dict              # Baseline portfolio weights, e.g., {"AAPL": 0.3, "MSFT": 0.25}
    params: Dict[str, Any] = {}        # Optional additional optimisation parameters (risk_aversion, baseline_reg, min/max weights)

# Payload to save an optimised portfolio
class SavePortfolioPayload(BaseModel):
    portfolio: Dict[str, Any]           # Full portfolio data including weights and parameters per strategy
    metadata: Optional[Dict[str, Any]] = {}  # Optional metadata such as author, notes, or tags
    timestamp: Optional[datetime] = None    # Timestamp of portfolio creation

# Output model for a saved portfolio
class PortfolioOut(BaseModel):
    id: int                             # Database ID of the portfolio
    data: dict                           # Stored portfolio data
    meta: Optional[dict] = None         # Optional metadata
    created_at: datetime                 # Timestamp of portfolio creation

    model_config = {
        "from_attributes": True          # Enable ORM mode for SQLAlchemy models
    }
