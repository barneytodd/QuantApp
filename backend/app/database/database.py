import logging
import os
import pyodbc
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Reduce SQLAlchemy engine logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Connection string for MS SQL Server
load_dotenv()  # load .env file

DB_ENGINE = os.getenv("DB_ENGINE", "mssql")

if DB_ENGINE == "sqlite":
    SQLALCHEMY_DATABASE_URL = "sqlite:///app/data/QuantApp.db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},  # required for SQLite threading
        echo=False
    )

else:
    DB_ENV = os.getenv("APP_ENV", "local")
    DB_USER = os.getenv("DB_LOCAL_USER") if DB_ENV == "local" else os.getenv("DB_DOCKER_USER")
    DB_PASSWORD = os.getenv("DB_LOCAL_PASSWORD") if DB_ENV == "local" else os.getenv("DB_DOCKER_PASSWORD")
    DB_HOST = os.getenv("DB_LOCAL_HOST") if DB_ENV == "local" else os.getenv("DB_DOCKER_HOST")
    DB_PORT = os.getenv("DB_PORT", "1433")
    DB_INSTANCE = os.getenv("DB_INSTANCE", "SQLEXPRESS")
    DB_NAME = os.getenv("DB_NAME")

    drivers = [driver for driver in pyodbc.drivers() if "SQL Server" in driver and "ODBC" in driver]
    if not drivers:
        raise RuntimeError("No SQL Server ODBC drivers found!")
    DB_DRIVER = sorted(drivers)[-1]

    server = f"{DB_HOST}\\{DB_INSTANCE}" if DB_ENV == "local" else f"{DB_HOST},{DB_PORT}"


    SQLALCHEMY_DATABASE_URL = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{server}/{DB_NAME}?driver={DB_DRIVER}&TrustServerCertificate=yes&Encrypt=no"
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
