from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String, nullable=False)  # Name of the trading strategy
    symbol = Column(String, nullable=False)         # The symbol the backtest ran on
    run_date = Column(DateTime, nullable=False)     # When the backtest was executed
    initial_capital = Column(Float)                 # Starting capital
    final_capital = Column(Float)                   # Ending capital after backtest
    return_pct = Column(Float)                      # Percentage return (final - initial / initial)
    sharpe_ratio = Column(Float)                    # Risk-adjusted return metric
