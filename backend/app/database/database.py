import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Reduce SQLAlchemy engine logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Connection string for MS SQL Server
SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc://quant_user:QuantProject!25@localhost\\SQLEXPRESS/QuantDB?driver=ODBC+Driver+17+for+SQL+Server"
)

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,            # number of connections to keep in the pool
    max_overflow=20,         # extra connections allowed beyond pool_size
    pool_pre_ping=True,      # ensures connections are alive before using
    fast_executemany=True,   # speeds up bulk inserts with pyodbc
    echo=False               # set True for SQL debug logs
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for FastAPI endpoints.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
