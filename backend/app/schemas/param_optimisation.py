from typing import Dict, Any, Optional, Union

from pydantic import BaseModel


class ParamOptimisationRequest(BaseModel):
    strategies: Dict[str, Any]                     
    globalParams: Dict[str, Any]
    optimParams: Dict[str, Any]
    scoringParams: Optional[Dict[str, Union[int, float]]] = None
