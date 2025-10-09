from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import logging

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Connection string for MS SQL Server
SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc://quant_user:QuantProject!25@localhost\\SQLEXPRESS/QuantDB?driver=ODBC+Driver+17+for+SQL+Server"
)

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db() -> Session:
    """
    Provide a database session to FastAPI endpoints.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
