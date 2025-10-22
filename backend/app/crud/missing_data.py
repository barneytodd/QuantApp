from app.models import MissingPriceRange

def insert_missing_data(db, symbol, start_date, end_date, error_message):
    record = MissingPriceRange(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        reason=error_message
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
