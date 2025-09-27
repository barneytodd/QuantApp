from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Leg:
    stock: str
    shares: float
    entry_price: float

@dataclass
class Position:
    symbol: str                     # e.g., "AAPL" or "AAPL-MSFT"
    legs: List[Leg]                 # one or more legs
    entry_date: str
    exit_date: Optional[str] = None
    closed: bool = False

    def mark_to_market(self, prices: Dict[str, float]) -> float:
        """Compute current value of all legs given prices dict {stock: price}"""
        return sum(leg.shares * prices[leg.stock] for leg in self.legs)

    def unrealized_pnl(self, prices: Dict[str, float]) -> float:
        """Compute current unrealized PnL"""
        return sum(leg.shares * (prices[leg.stock] - leg.entry_price) for leg in self.legs)
