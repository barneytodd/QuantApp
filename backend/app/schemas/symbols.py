from pydantic import BaseModel
from typing import Dict, Any, Optional

# Request model for running a strategy backtest
class SymbolsRequest(BaseModel):
    filters: Dict[str, Any]
