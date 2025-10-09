from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

class PreScreenPayload(BaseModel):
    symbols: List[str]                      
    start: date
    end: date
    filters: Dict[str, Any]