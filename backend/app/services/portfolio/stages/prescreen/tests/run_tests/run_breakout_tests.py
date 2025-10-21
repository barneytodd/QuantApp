from ..momentum_tests import min_volatility_test

# === Breakout Strategy Heuristic Test Engine ===

def run_breakout_tests(short_vol: float, long_vol: float, filters: dict) -> dict:
    """
    Run heuristic breakout suitability tests on a stock.

    The function checks if a stock is suitable for breakout strategies
    based on volatility and other numeric thresholds.

    Current implemented test:
        1. Minimum volatility test - ensures the stock has sufficient price movement
           to support breakout strategies.

    Args:
        short_vol: float, annualized short-term volatility of the stock
        long_vol: float, annualized long-term volatility of the stock
        filters: dict, numeric thresholds for each breakout test, e.g.,
            {"minVolatilityBreakout": 0.2}

    Returns:
        dict:
            result: bool, True if all tests pass, False otherwise
            test: optional string, name of the failed test if any
    """

    # --- Test 1: Minimum volatility ---
    if not min_volatility_test(short_vol, long_vol, filters["minVolatilityBreakout"]):
        return {
            "result": False,
            "test": "minVolatilityBreakoutTestFailed"
        }

    # --- All tests passed ---
    return {"result": True}
