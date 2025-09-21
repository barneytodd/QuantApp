from pydantic import BaseModel
from typing import List

# Request model for cointegration analysis
class CointegrationRequest(BaseModel):
    y: List[float]
    x: List[float]
