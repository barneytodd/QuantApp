from sqlalchemy import Column, String, Float, Integer, Date, UniqueConstraint
from app.database import Base

# ORM model for historical OHLCV price data
class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint("symbol", "date", name="uix_symbol_date"), {"schema": "dbo", "extend_existing": True})

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
