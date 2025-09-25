from pydantic import BaseModel
from typing import List, Dict, Any

class ParamOptimisationRequest(BaseModel):
    strategy: str                      
    symbols: List[str]
    params: Dict[str, Any]
    optimParams: Dict[str, Any]
