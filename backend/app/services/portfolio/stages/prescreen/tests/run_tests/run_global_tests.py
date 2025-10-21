from ..global_tests import bid_ask_test, max_drawdown_test, skewness_test, kurtosis_test, max_volatility_test

# === Global Heuristic Test Engine ===

def run_global_tests(
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
    Run a series of global heuristic tests on stock data to eliminate unsuitable symbols.

    The function checks the following:
        1. Bid-ask spread      - ensures average spread is below a maximum threshold.
        2. Maximum drawdown    - ensures historical losses stay within acceptable limits.
        3. Skewness            - verifies return distribution is not overly negative.
        4. Kurtosis            - checks for fat tails or extreme return outliers.
        5. Volatility          - ensures both short- and long-term volatility are below thresholds.

    Args:
        short_start: datetime, start date for short-term analysis window
        long_start: datetime, start date for long-term analysis window
        short_data: list[dict], recent price data (e.g., last year)
        long_data: list[dict], longer historical price data (e.g., last 3–5 years)
        short_vol: float, annualized short-term volatility
        long_vol: float, annualized long-term volatility
        short_returns: list[float], daily returns in short-term window
        long_returns: list[float], daily returns in long-term window
        filters: dict, numeric thresholds for each test (e.g., maxBidAsk, maxDrawdown, skewness, kurtosis, maxVolatility)

    Returns:
        dict:
            result: bool, True if all tests pass, False otherwise
            test: optional string, name of failed test if any
    """

    # --- Test 1: Bid-ask spread ---
    if not bid_ask_test(long_data, short_start, long_start, filters["maxBidAsk"]):
        return {"result": False, "test": "bidAskTestFailed"}

    # --- Test 2: Maximum drawdown ---
    if not max_drawdown_test(long_data, long_start, filters["maxDrawdown"]):
        return {"result": False, "test": "maxDrawdownTestFailed"}

    # --- Test 3: Skewness of returns ---
    if not skewness_test(short_returns, long_returns, filters["skewness"]):
        return {"result": False, "test": "skewnessTestFailed"}

    # --- Test 4: Kurtosis of returns ---
    if not kurtosis_test(short_returns, long_returns, filters["kurtosis"]):
        return {"result": False, "test": "kurtosisTestFailed"}

    # --- Test 5: Maximum volatility ---
    if not max_volatility_test(short_vol, long_vol, filters["maxVolatility"]):
        return {"result": False, "test": "maxVolatilityTestFailed"}

    # --- All tests passed ---
    return {"result": True}
