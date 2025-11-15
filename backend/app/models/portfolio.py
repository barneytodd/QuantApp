from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, JSON
from app.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)  # Primary key, auto-increment
    data = Column(JSON, nullable=False)                 # Stores the portfolio content
    meta = Column(JSON, nullable=True)                 # Optional metadata
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))      # Timestamp of creation
