from ..mean_reversion_tests import autocorrelation_test, zscore_reversion_test

def run_mean_reversion_tests(short_start, long_start, long_data, short_returns, long_returns, filters):
    """
    Runs a series of mean-reversion heuristic tests on a stock to assess suitability for
    mean-reverting strategies.

    The function checks:
      1. Lag-1 autocorrelation - ensures returns exhibit negative autocorrelation (mean-reverting behavior).
      2. Z-score reversion - checks how often prices revert toward their moving average
         after deviating beyond a specified Z-score threshold.

    Parameters:
        short_start (datetime): Start date for short-term analysis window.
        long_start (datetime): Start date for long-term analysis window.
        long_data (list[dict]): Historical price data (e.g., last 3-5 years), each with 'date' and 'close'.
        short_returns (list[float]): Daily returns in the short-term window.
        long_returns (list[float]): Daily returns in the long-term window.
        filters (dict): Dictionary containing thresholds for each mean-reversion test, including:
            - "autocorrelation": Maximum acceptable lag-1 autocorrelation
            - "zscoreThreshold": Z-score deviation to define extreme price movements
            - "zscoreReversion": Minimum proportion of reversions required to pass

    Returns:
        bool: True if the stock passes all mean-reversion heuristic tests, False otherwise.
    """

    if not autocorrelation_test(short_returns, long_returns, filters["autocorrelation"]):
        return {"result": False, "test": "autocorrelationTestFailed"}
    
    if not zscore_reversion_test(long_data, short_start, long_start, z_threshold=filters["zscoreThreshold"], threshold=filters["zscoreReversion"]):
        return {"result": False, "test": "zscoreReversionTestFailed"}
    
    return {"result": True}