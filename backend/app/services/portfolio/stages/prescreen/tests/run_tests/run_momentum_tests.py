from ..momentum_tests import above_MA_test, av_slope_test, pos_returns_test, min_volatility_test
from app.utils.indicators import compute_sma

# === Momentum Heuristic Test Engine ===

def run_momentum_tests(
    short_start,
    long_start,
    short_data,
    long_data,
    short_vol,
    long_vol,
    short_returns,
    long_returns,
    filters
) -> dict:
    """
    Run momentum-based heuristic tests on a stock to assess trend-following viability.

    The function checks the following:
        1. Price relative to moving average (MA) - ensures the stock is above its MA
           for a sufficient percentage of time.
        2. Moving average slope - verifies the MA has a positive trend over both
           long and short periods.
        3. Positive daily returns - confirms consistent upward movement.
        4. Minimum volatility - ensures sufficient price movement to support momentum strategies.

    Args:
        short_start: datetime, start date for short-term analysis window
        long_start: datetime, start date for long-term analysis window
        short_data: list[dict], recent price data (e.g., last year)
        long_data: list[dict], longer historical price data (e.g., last 3–5 years)
        short_vol: float, annualized short-term volatility
        long_vol: float, annualized long-term volatility
        short_returns: list[float], daily returns in short-term window
        long_returns: list[float], daily returns in long-term window
        filters: dict, thresholds for each momentum test, e.g.,
            - "percentageAboveMA": min % time above MA
            - "avSlope": min average slope of MA
            - "posReturns": min % positive returns
            - "minVolatilityMomentum": min required volatility

    Returns:
        dict:
            result: bool, True if all tests pass, False otherwise
            test: optional string, name of failed test if any
    """

    # --- Compute 200-day moving average ---
    try:
        MA = {row["date"]: row["value"] for row in compute_sma(long_data, 200)}
    except Exception:
        MA = None

    # --- Test 1: Price above moving average ---
    if MA and not above_MA_test(long_data, MA, short_start, long_start, filters["percentageAboveMA"]):
        return {"result": False, "test": "aboveMATestFailed"}

    # --- Test 2: Moving average slope ---
    if MA and not av_slope_test(MA, short_start, long_start, filters["avSlope"]):
        return {"result": False, "test": "avSlopeTestFailed"}

    # --- Test 3: Positive daily returns ---
    if not pos_returns_test(short_returns, long_returns, filters["posReturns"]):
        return {"result": False, "test": "posReturnsTestFailed"}

    # --- Test 4: Minimum volatility ---
    if not min_volatility_test(short_vol, long_vol, filters["minVolatilityMomentum"]):
        return {"result": False, "test": "minVolatilityMomentumTestFailed"}

    # --- All tests passed ---
    return {"result": True}
