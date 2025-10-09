from ..global_tests import bid_ask_test, max_drawdown_test, skewness_test, kurtosis_test, max_volatility_test

def run_global_tests(short_start, long_start, short_data, long_data, short_vol, long_vol, filters):
    """
    Runs a series of global heuristic tests on stock data to quickly eliminate unsuitable symbols.

    The function checks:
      1. Bid-ask spread - ensures average spread is below a maximum threshold.
      2. Maximum drawdown - ensures historical losses stay within acceptable limits.
      3. Skewness - verifies distribution of returns is not overly negative.
      4. Kurtosis - checks for fat tails or extreme return outliers.
      5. Volatility - ensures both short- and long-term volatility are below a maximum threshold.

    Parameters:
        short_start (datetime): Start date for short-term analysis window.
        long_start (datetime): Start date for long-term analysis window.
        short_data (list[dict]): Recent price data (e.g., last year).
        long_data (list[dict]): Longer historical price data (e.g., last 3-5 years).
        short_vol (float): Annualized short-term volatility.
        long_vol (float): Annualized long-term volatility.
        filters (dict): Dictionary containing numeric thresholds for each test.

    Returns:
        bool: True if the symbol passes all global heuristic tests, False otherwise.
    """

    if not bid_ask_test(long_data, short_start, long_start, filters["maxBidAsk"]):
        return False

    if not max_drawdown_test(long_data, long_start, filters["maxDrawdown"]):
        return False

    if not skewness_test(short_data, long_data, filters["skewness"]):
        return False

    if not kurtosis_test(short_data, long_data, filters["kurtosis"]):
        return False

    if not max_volatility_test(short_vol, long_vol, filters["maxVolatility"]):
        return False

    return True
