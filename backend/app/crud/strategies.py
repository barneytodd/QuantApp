from sqlalchemy.orm import Session

from app.models.strategies import BacktestResult
from app.schemas.backtesting.backtest import BacktestResultIn


# === Save a single backtest result ===
def save_backtest_result(db: Session, result: BacktestResultIn) -> BacktestResult:
    """
    Save a BacktestResultIn object into the database.

    Args:
        db: SQLAlchemy session
        result: BacktestResultIn schema object containing the backtest result

    Returns:
        The persisted BacktestResult ORM object
    """
    db_result = BacktestResult(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


# === Retrieve all backtest results for a specific strategy ===
def get_backtest_results(db: Session, strategy_name: str):
    """
    Fetch all backtest results associated with a given strategy name.

    Args:
        db: SQLAlchemy session
        strategy_name: Name of the strategy to filter by

    Returns:
        List of BacktestResult ORM objects
    """
    return db.query(BacktestResult).filter(
        BacktestResult.strategy_name == strategy_name
    ).all()
