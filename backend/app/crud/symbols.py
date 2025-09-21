from sqlalchemy.orm import Session
from app.models import Price

# Retrieve all distinct symbols from the Price table
def get_all_symbols(db: Session):
    rows = db.query(Price.symbol).distinct().all()
    return [r[0] for r in rows]
