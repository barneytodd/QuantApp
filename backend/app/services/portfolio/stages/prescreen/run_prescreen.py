# app/services/portfolio/stages/prescreen/run_prescreen.py
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
import numpy as np
from threading import Lock
import os
import sys
from app.tasks import tasks_store

from .tests.run_tests import run_breakout_tests, run_global_tests, run_mean_reversion_tests, run_momentum_tests

def test_symbol(symbol, symbol_data, filters):
    start_time = datetime.now().isoformat()

    symbol_results = {"global": True, "momentum": True, "mean_reversion": True, "breakout": True}
    fails = {"global": [], "momentum": [], "mean_reversion": [], "breakout": []}
    
    try:
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

    end_time = datetime.now().isoformat()
    return symbol, symbol_results, fails, start_time, end_time


def run_tests(data, filters, max_workers=5, progress_callback=None, task_id=None):
    
    results = {}
    total_symbols = len(data)
    failed_count = {}
    testing_count = 0
    completed_count = 0
    lock = Lock()

    total_tests = total_symbols  # if updating per symbol; multiply by 4 if per test

    def _update_progress():
        """Send current progress to frontend"""
        if progress_callback:
            progress_callback({
                "testing": testing_count,
                "completed": completed_count,
                "total": total_symbols
            })

    symbols_iter = iter(data.items())

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        in_flight = {}
        
        # Initial submission: fill up to max_workers
        for _ in range(min(max_workers, total_symbols)):
            try:
                sym, sym_data = next(symbols_iter)
                future = executor.submit(test_symbol, sym, sym_data, filters)
                in_flight[future] = sym
                with lock:
                    testing_count += 1
                    _update_progress()
            except StopIteration:
                break

        while in_flight:
            for future in as_completed(list(in_flight.keys())):
                sym = in_flight.pop(future)
                try:
                    sym, res, fails, start_time, end_time = future.result()
                    results[sym] = res
                except Exception as e:
                    results[sym] = {"error": str(e)}
                    fails = ["exception"]

                # Update tasks_store and progress
                with lock:
                    if task_id is not None:
                        tasks_store[task_id]["results"][sym] = res
                        for group, fail_list in fails.items():
                            for fail in fail_list:
                                tasks_store[task_id]["fails"][group][fail] = tasks_store[task_id]["fails"][group].get(fail, 0) + 1
                    testing_count -= 1
                    completed_count += 1
                    _update_progress()

                # Submit the next symbol from iterator
                try:
                    sym, sym_data = next(symbols_iter)
                    future = executor.submit(test_symbol, sym, sym_data, filters)
                    in_flight[future] = sym
                    with lock:
                        testing_count += 1
                        _update_progress()
                except StopIteration:
                    pass
                break  # exit inner loop to reevaluate in_flight
            
    return results, failed_count

