# app/services/portfolio/stages/prescreen/run_prescreen.py
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
import asyncio
from datetime import datetime, timedelta
import numpy as np
from app.tasks import prescreen_tasks_store as tasks_store
from app import crud
from app.database import SessionLocal
from app.database_async import get_connection, release_connection, init_db_pool, close_db_pool
import itertools
import time

from .tests.run_tests import run_breakout_tests, run_global_tests, run_mean_reversion_tests, run_momentum_tests


def test_symbol(symbol, symbol_data, filters):
    start_time = datetime.now().isoformat()

    try:
        symbol_results = {"global": True, "momentum": True, "mean_reversion": True, "breakout": True}
        fails = {"global": [], "momentum": [], "mean_reversion": [], "breakout": []}

        today = datetime.today()
        short_start = (today - timedelta(days=round(0.5 * 365))).date()
        long_start = (today - timedelta(days=round(3 * 365))).date()

        short_data = [row for row in symbol_data if row["date"] >= short_start]
        long_data = [row for row in symbol_data if row["date"] >= long_start]

        short_volatility = np.std([d["close"] for d in short_data], ddof=1) if short_data else 0
        long_volatility = np.std([d["close"] for d in long_data], ddof=1) if long_data else 0

        def prices_to_returns(data):
            closes = [row["close"] for row in data if "close" in row and row["close"] is not None]
            return np.diff(closes) / closes[:-1] if len(closes) > 1 else np.array([])

        short_returns = prices_to_returns(short_data)
        long_returns = prices_to_returns(long_data)

        global_result = run_global_tests(short_start, long_start, short_data, long_data, short_volatility, long_volatility, short_returns, long_returns, filters)
        if not global_result["result"]:
            symbol_results["global"] = False
            fails["global"].append(global_result["test"])
            end_time = datetime.now().isoformat()
            return symbol, symbol_results, fails, start_time, end_time

        momentum_result = run_momentum_tests(short_start, long_start, short_data, long_data, short_volatility, long_volatility, short_returns, long_returns, filters)
        if not momentum_result["result"]:
            symbol_results["momentum"] = False
            fails["momentum"].append(momentum_result["test"])

        mean_reversion_result = run_mean_reversion_tests(short_start, long_start, long_data, short_returns, long_returns, filters)
        if not mean_reversion_result["result"]:
            symbol_results["mean_reversion"] = False
            fails["mean_reversion"].append(mean_reversion_result["test"])

        breakout_result = run_breakout_tests(short_volatility, long_volatility, filters)
        if not breakout_result["result"]:
            symbol_results["breakout"] = False
            fails["breakout"].append(breakout_result["test"])

    except Exception as e:
        symbol_results = {"error": str(e)}
        fails = {"global": [str(e)], "momentum": [], "mean_reversion": [], "breakout": []}


    end_time = datetime.now().isoformat()
    return symbol, symbol_results, fails, start_time, end_time


async def fetch_prices(symbols, start, end, queue: asyncio.Queue, stop_signal, lock, completed_count, testing_count, progress_callback, batch_size=25, task_id=None):
    """Stream batches of prices into the queue."""
    symbols_iter = iter(symbols)
    consecutive_fast = consecutive_slow = 0

    while True:
        batch = list(itertools.islice(symbols_iter, batch_size))
        if not batch:
            break

        conn = await get_connection()
        cursor = await conn.cursor()
        try:
            placeholders = ", ".join(["?"] * len(batch))
            sql = f"""
                SELECT symbol, [date], [close], [high], [low]
                FROM dbo.prices WITH (NOLOCK)
                WHERE symbol IN ({placeholders})
                  AND [date] BETWEEN ? AND ?
                ORDER BY symbol, [date];
            """

            t0 = time.perf_counter()
            await cursor.execute(sql, (*batch, start, end))
            rows = await cursor.fetchall()
            t1 = time.perf_counter()

            batch_symbols = set(batch)
            returned_symbols = set(r[0] for r in rows)
            missing_symbols = batch_symbols - returned_symbols

            # Update tasks_store and completed count for missing symbols
            if task_id is not None and missing_symbols:
                async with lock:
                    for sym in missing_symbols:
                        tasks_store[task_id]["results"][sym] = {
                            "global": False,
                            "momentum": True,
                            "mean_reversion": True,
                            "breakout": True
                        }
                        tasks_store[task_id]["fails"]["global"]["no data"] = \
                            tasks_store[task_id]["fails"]["global"].get("no data", 0) + 1
                        completed_count["value"] += 1

                    if progress_callback:
                        progress_callback({
                            "testing": testing_count["value"],
                            "completed": completed_count["value"],
                            "total": len(symbols),
                        })

            await queue.put(rows)

            elapsed = t1 - t0
            # Dynamic batch size adaptation
            if elapsed < 0.5 and batch_size < 100:
                consecutive_fast += 1
                consecutive_slow = 0
                if consecutive_fast >= 3:
                    batch_size *= 2
                    consecutive_fast = 0
            elif elapsed > 2.0 and batch_size > 5:
                consecutive_slow += 1
                consecutive_fast = 0
                if consecutive_slow >= 2:
                    batch_size //= 2
                    consecutive_slow = 0

        except Exception as e:
            print(f"[fetch_prices] Error fetching batch: {e}")
        finally:
            await cursor.close()
            await release_connection(conn)

    # Signal the consumer to stop
    await queue.put(stop_signal)


async def run_tests_async(symbols, start, end, filters, max_workers=5, progress_callback=None, task_id=None):
    """Run tests while streaming price data from SQL."""

    queue = asyncio.Queue(maxsize=50)
    stop_signal = object()
    results = {}
    failed_count = {}
    testing_count = {"value": 0}
    completed_count = {"value": 0}
    lock = asyncio.Lock()

    async def update_progress():
        if progress_callback:
            progress_callback({
                "testing": testing_count["value"],
                "completed": completed_count["value"],
                "total": len(symbols),
            })


    fetch_task = asyncio.create_task(fetch_prices(symbols, start, end, queue, stop_signal, lock, completed_count, testing_count, progress_callback, batch_size = 25, task_id=task_id))

    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        in_flight = {}

        async def check_done():
            """Check completed futures and update results."""
            nonlocal testing_count, completed_count
            finished = [f for f in in_flight if f.done()]
            for f in finished:
                sym = in_flight.pop(f)
                try:
                    sym, res, fails, _, _ = f.result()
                except Exception as e:
                    res = {"error": str(e)}
                    fails = {"global": [str(e)], "momentum": [], "mean_reversion": [], "breakout": []}

                async with lock:
                    testing_count["value"] -= 1
                    completed_count["value"] += 1
                    results[sym] = res
                    if task_id is not None:
                        tasks_store[task_id]["results"][sym] = res
                        for group_name, fail_list in fails.items():
                            for fail in fail_list:
                                d = tasks_store[task_id]["fails"][group_name]
                                d[fail] = d.get(fail, 0) + 1
                    await update_progress()

        while True:
            batch = await queue.get()
            if batch is stop_signal:
                break

            # group rows by symbol
            grouped = {}
            for r in batch:
                grouped.setdefault(r[0], []).append({
                    "symbol": r[0],
                    "date": r[1],
                    "close": r[2],
                    "high": r[3],
                    "low": r[4],
                })
            

            for sym, data in grouped.items():
                # throttle submission
                while len(in_flight) >= max_workers * 2:
                    await asyncio.sleep(0.1)
                    await check_done()

                fut = executor.submit(test_symbol, sym, data, filters)
                in_flight[fut] = sym
                async with lock:
                    testing_count["value"] += 1
                    await update_progress()

            await check_done()

        print("--------------", in_flight.keys())
        # Wait for any remaining tasks
        while in_flight:
            # Copy keys to avoid mutation issues
            futures_snapshot = list(in_flight.keys())

            for f in futures_snapshot:
                if f.done():
                    sym = in_flight.pop(f)
                    try:
                        sym, res, fails, _, _ = f.result()
                    except Exception as e:
                        res = {"error": str(e)}
                        fails = {"global": [str(e)], "momentum": [], "mean_reversion": [], "breakout": []}

                    async with lock:
                        testing_count["value"] -= 1
                        completed_count["value"] += 1
                        results[sym] = res
                        if task_id is not None:
                            tasks_store[task_id]["results"][sym] = res
                            for group_name, fail_list in fails.items():
                                for fail in fail_list:
                                    d = tasks_store[task_id]["fails"][group_name]
                                    d[fail] = d.get(fail, 0) + 1
                        await update_progress()

            # small sleep to avoid busy loop
            await asyncio.sleep(0.05)
    print("All tasks completed.")
    await fetch_task  # ensure fetcher finishes cleanly

    return results, failed_count


async def run_tests(symbols, start, end, filters, max_workers=5, progress_callback=None, task_id=None):
    return await run_tests_async(symbols, start, end, filters, max_workers, progress_callback, task_id)
