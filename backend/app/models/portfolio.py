from sqlalchemy import Column, Integer, DateTime, JSON
from app.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)