from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, timedelta
from .tests.run_tests.run_global_tests import run_global_tests
import numpy as np
from .tests.run_tests import run_breakout_tests, run_global_tests, run_mean_reversion_tests, run_momentum_tests


def run_tests(data, filters, max_workers=5):
    """
    Run a series of tests on grouped symbol data in parallel.

    Parameters:
    - data: dict of {symbol: list_of_ohlcv_dicts}
    - filters: dict of {filter: value}
    - max_workers: number of threads for parallel execution

    Returns:
    - dict of {symbol: test_results}
    """
    results = {}

    def test_symbol(symbol, symbol_data, filters, short_period=0.5, long_period=3):
        """
        Perform all tests for a single symbol.
        Returns a dict with test results.
        """
        symbol_results = {"global": True, "momentum": True, "mean_reversion": True, "breakout": True}

        today = datetime.today()
        short_start =  (today - timedelta(days=round(short_period*365))).date()
        long_start = (today - timedelta(days=round(long_period*365))).date()

        short_data = [row for row in symbol_data if row["date"] >= short_start]
        long_data = [row for row in symbol_data if row["date"] >= long_start]

        short_volatility = np.std([d["close"] for d in short_data], ddof=1)
        long_volatility = np.std([d["close"] for d in long_data], ddof=1)
        
        if not run_global_tests(short_start, long_start, short_data, long_data, short_volatility, long_volatility, filters):
            symbol_results["global"] = False
            return symbol_results
        
        if not run_momentum_tests(short_start, long_start, short_data, long_data, short_volatility, long_volatility, filters):
            symbol_results["momentum"] = False

        if not run_mean_reversion_tests(short_start, long_start, long_data, filters):
            symbol_results["mean_reversion"] = False

        if not run_breakout_tests(short_volatility, long_volatility, filters):
            symbol_results["breakout"] = False

        return symbol_results

    # Run tests in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {executor.submit(test_symbol, sym, sym_data, filters): sym for sym, sym_data in data.items()}

        for future in as_completed(future_to_symbol):
            sym = future_to_symbol[future]
            try:
                results[sym] = future.result()
            except Exception as e:
                results[sym] = {"error": str(e)}

    return results