from sqlalchemy.orm import Session

from app.models.strategies import BacktestResult
from app.schemas.strategies import BacktestResultIn


# Save a backtest result to the database
def save_backtest_result(db: Session, result: BacktestResultIn):
    db_result = BacktestResult(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

# Retrieve all backtest results for a given strategy
def get_backtest_results(db: Session, strategy_name: str):
    return db.query(BacktestResult).filter(
        BacktestResult.strategy_name == strategy_name
    ).all()
