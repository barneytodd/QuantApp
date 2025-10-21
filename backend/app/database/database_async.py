import aioodbc
import asyncio

# === Database connection string ===
dsn = (
    "Driver=ODBC Driver 17 for SQL Server;"
    "Server=localhost\\SQLEXPRESS;"
    "Database=QuantDB;"
    "UID=quant_user;"
    "PWD=QuantProject!25;"
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
