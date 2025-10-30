from datetime import date
from pydantic import BaseModel

class StatsOut(BaseModel):
    symbol: str                          # Trading symbol
    start_date: date                      # Start date of data
    end_date: date                        # End date of data
    annualised_volatility: float          # Annualised standard deviation of returns
    mean_return: float                    # Average annualised return
    sharpe_ratio: float                   # Risk-adjusted return
    max_drawdown: float                   # Maximum drawdown observed

    model_config = {
        "from_attributes": True
    }