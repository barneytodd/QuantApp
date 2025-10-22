from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from app.database import Base


class MissingPriceRange(Base):
    __tablename__ = "missing_price_ranges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False)  # ✅ use bounded length
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("symbol", "start_date", "end_date", name="_symbol_start_end_uc"),
    )
