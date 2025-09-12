# Connect to the SQL database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string for db
SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc://quant_user:QuantProject!25@localhost\SQLEXPRESS/QuantDB?driver=ODBC+Driver+17+for+SQL+Server"
)

# Creates a connection engine to db
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True) 

# Creates a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creates a base class which is inherited by all table classes
Base = declarative_base()