from typing import Dict, Any

from pydantic import BaseModel


# Request model for running a strategy backtest
class SymbolsRequest(BaseModel):
    filters: Dict[str, Any]
