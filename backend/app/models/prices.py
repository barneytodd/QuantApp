from sqlalchemy import Column, String, Float, Integer, Date, UniqueConstraint
from app.database import Base

class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uix_symbol_date"),  # Ensure no duplicates per symbol per date
        {"schema": "dbo", "extend_existing": True}  # Use 'dbo' schema in SQL Server
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
