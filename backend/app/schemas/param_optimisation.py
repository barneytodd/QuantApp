from pydantic import BaseModel
from typing import List, Dict, Any

class ParamOptimisationRequest(BaseModel):
    strategies: Dict[str, Any]                     
    globalParams: Dict[str, Any]
    optimParams: Dict[str, Any]
