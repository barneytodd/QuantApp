from pydantic import BaseModel
from typing import List

class PairSelectionRequest(BaseModel):
    symbols: List[str]                      
    w_corr: float = 0.5
    w_coint: float = 0.5
