from dotenv import load_dotenv
import os
import pyodbc

import aioodbc
import asyncio

# === Database connection string ===
load_dotenv()  # load .env file

DB_ENV = os.getenv("DB_ENV", "local")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_LOCAL_HOST") if DB_ENV == "local" else os.getenv("DB_DOCKER_HOST")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_INSTANCE = os.getenv("DB_INSTANCE", "SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME")

server = f"{DB_HOST}\\{DB_INSTANCE}" if DB_ENV == "local" else f"{DB_HOST},{DB_PORT}"

drivers = [driver for driver in pyodbc.drivers() if "SQL Server" in driver and "ODBC" in driver]
if not drivers:
    raise RuntimeError("No SQL Server ODBC drivers found!")
DB_DRIVER = sorted(drivers)[-1]

dsn = (
    f"Driver={DB_DRIVER};"
    f"Server={server};"
    f"Database={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    "TrustServerCertificate=yes;"
)

_pool = None
_pool_lock = asyncio.Lock()


async def init_db_pool(minsize: int = 1, maxsize: int = 10) -> aioodbc.Pool:
    """
    Initialize the global aioodbc connection pool.

    Returns:
        The initialized pool.
    """
    global _pool
    async with _pool_lock:
        if _pool is None:
            _pool = await aioodbc.create_pool(
                dsn=dsn,
                minsize=minsize,
                maxsize=maxsize,
                autocommit=True
            )
    return _pool


async def close_db_pool():
    """Close the global connection pool if it exists."""
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


async def get_connection() -> aioodbc.Connection:
    """
    Acquire a connection from the global pool.

    Raises:
        RuntimeError if the pool has not been initialized.
    """
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return await _pool.acquire()


async def release_connection(conn: aioodbc.Connection):
    """Release a connection back to the global pool."""
    if _pool is not None and conn is not None:
        await _pool.release(conn)
