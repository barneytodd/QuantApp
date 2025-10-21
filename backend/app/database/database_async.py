import aioodbc
import asyncio

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

async def init_db_pool(minsize=1, maxsize=10):
    global _pool
    async with _pool_lock:
        if _pool is None:
            _pool = await aioodbc.create_pool(
                dsn=dsn, minsize=minsize, maxsize=maxsize, autocommit=True
            )
    return _pool

async def close_db_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None

async def get_connection():
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return await _pool.acquire()

async def release_connection(conn):
    if _pool is not None:
        await _pool.release(conn)
