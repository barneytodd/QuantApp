from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database import Base

# ORM model for storing backtest results of trading strategies
class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    run_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float)
    final_capital = Column(Float)
    return_pct = Column(Float)
    sharpe_ratio = Column(Float)
