from ..mean_reversion_tests import autocorrelation_test, zscore_reversion_test

# === Mean-Reversion Heuristic Test Engine ===

def run_mean_reversion_tests(
    short_start,
    long_start,
    long_data,
    short_returns,
    long_returns,
    filters
) -> dict:
    """
    Run heuristic mean-reversion tests on a stock to assess suitability for
    mean-reverting trading strategies.

    The function checks the following:
        1. Lag-1 autocorrelation   - ensures returns exhibit negative autocorrelation
                                     (mean-reverting behavior)
        2. Z-score reversion       - measures how often prices revert toward their moving
                                     average after deviating beyond a Z-score threshold

    Args:
        short_start: datetime, start date for short-term analysis window
        long_start: datetime, start date for long-term analysis window
        long_data: list[dict], historical price data with 'date' and 'close'
        short_returns: list[float], daily returns in short-term window
        long_returns: list[float], daily returns in long-term window
        filters: dict, thresholds for each mean-reversion test, e.g.,
            - "autocorrelation": maximum acceptable lag-1 autocorrelation
            - "zscoreThreshold": Z-score deviation to define extreme price movements
            - "zscoreReversion": minimum proportion of reversions required to pass

    Returns:
        dict:
            result: bool, True if all tests pass, False otherwise
            test: optional string, name of failed test if any
    """

    # --- Test 1: Lag-1 autocorrelation ---
    if not autocorrelation_test(short_returns, long_returns, filters["autocorrelation"]):
        return {"result": False, "test": "autocorrelationTestFailed"}

    # --- Test 2: Z-score reversion ---
    if not zscore_reversion_test(
        long_data,
        short_start,
        long_start,
        z_threshold=filters["zscoreThreshold"],
        threshold=filters["zscoreReversion"]
    ):
        return {"result": False, "test": "zscoreReversionTestFailed"}

    # --- All tests passed ---
    return {"result": True}
