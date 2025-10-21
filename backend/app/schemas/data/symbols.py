from typing import Dict, Any
from pydantic import BaseModel

# Request model to fetch symbols based on filtering criteria
class SymbolsRequest(BaseModel):
    filters: Dict[str, Any]  # Dictionary of filter criteria, e.g., {"region": ["US"], "exchange": ["NMS"]}
