from typing import Dict, Any, Optional, Union
from pydantic import BaseModel

class ParamOptimisationRequest(BaseModel):
    # Dictionary of strategies with their specific parameters
    strategies: Dict[str, Any]
    
    # Global parameters applied to all strategies
    globalParams: Dict[str, Any]
    
    # Parameters to optimize, e.g., ranges for each strategy parameter
    optimParams: Dict[str, Any]
    
    # Optional scoring weights for evaluating strategies (values between 0 and 1)
    scoringParams: Optional[Dict[str, Union[int, float]]] = None

    # Optional metric ranges for computing trial scores
    metricRanges: Optional[Dict[str, Any]]

    # Extra JSON schema for API documentation (FastAPI/OpenAPI)
    model_config = {
        "json_schema_extra": {
            "example": {
                "strategies": {"strategy1": {"param1": 10, "param2": 0.5}},
                "globalParams": {"capital": 100000, "risk_free_rate": 0.01},
                "optimParams": {"param1": [1, 10], "param2": [0.1, 1.0]},
                "scoringParams": {
                    "sharpe": 0.5,
                    "cagr": 0.3,
                    "max_drawdown": 0.2,
                    "win_rate": 0.1
                }
            }
        }
    }
