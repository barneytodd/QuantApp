from ..momentum_tests import min_volatility_test

def run_breakout_tests(short_vol, long_vol, filters):
    """
    Runs a series of breakout - based heuristic tests on a stock to test suitability for breakout strategies.

    The function checks:
      1. Minimum volatility - ensures the stock has enough price movement to support breakout strategies.

    Parameters:
        short_vol (float): Annualized short-term volatility.
        long_vol (float): Annualized long-term volatility.
        filters (dict): Dictionary containing numeric thresholds for each breakout test.

    Returns:
        bool: True if the stock passes all breakout heuristic tests, False otherwise.
    """
    
    if not min_volatility_test(short_vol, long_vol, filters["minVolatilityBreakout"]):
	    return {"result": False, "test": "minVolatilityBreakoutTestFailed"}
    
    return {"result": True}