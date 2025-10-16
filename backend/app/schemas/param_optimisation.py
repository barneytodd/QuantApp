from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

class ParamOptimisationRequest(BaseModel):
    strategies: Dict[str, Any]                     
    globalParams: Dict[str, Any]
    optimParams: Dict[str, Any]
    scoringParams: Optional[Dict[str, Union[int, float]]] = None
