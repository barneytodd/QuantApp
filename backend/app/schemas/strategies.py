from typing import List, Dict, Any, Optional

from pydantic import BaseModel


# Request model for running a strategy backtest
class StrategyRequest(BaseModel):
    symbolItems: List[Dict[str, Any]]
    params: Dict[str, Any]

# Response model for backtest results
class StrategyResponse(BaseModel):
    symbol: str                    
    initialCapital: float
    finalCapital: float
    returnPct: float
    equityCurve: List[float]
    trades: Optional[List[Dict[str, Any]]] = []
    metrics: Dict[str, Any]        
    tradeStats: Dict[str, Any]     

    model_config = {
        "from_attributes": True
    }

# Internal model for backtest results used within the application
class BacktestResultIn(BaseModel):
    strategy_name: str
    data: Dict[str, Any]  
    initial_capital: float
    final_capital: float
    return_pct: float
    equity_curve: list
    trades: list

    model_config = {
        "from_attributes": True
    }