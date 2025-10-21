from sqlalchemy.orm import Session
from app.models import Price

# === Retrieve all unique symbols stored in the database ===
def get_all_symbols(db: Session) -> list[str]:
    """
    Fetch all distinct stock symbols from the Price table.

    Args:
        db: SQLAlchemy session

    Returns:
        A list of unique symbol strings
    """
    rows = db.query(Price.symbol).distinct().all()
    return [r[0] for r in rows]
