from ..momentum_tests import above_MA_test, av_slope_test, pos_returns_test, min_volatility_test
from app.utils.indicators import compute_sma

def run_momentum_tests(short_start, long_start, short_data, long_data, short_vol, long_vol, filters):
    """
    Runs a series of momentum-based heuristic tests on a stock to assess trend-following viability.

    The function checks:
      1. Price relative to moving average - ensures the stock is above its MA for a sufficient percentage of time.
      2. Moving average slope - verifies that the MA has a positive trend over long and short periods.
      3. Positive daily returns - confirms that the stock shows consistent upward movement.
      4. Minimum volatility - ensures the stock has enough price movement to support momentum strategies.

    Parameters:
        MA (dict): Mapping of date -> moving average value (e.g., 200-day MA).
        short_start (datetime): Start date for short-term analysis window.
        long_start (datetime): Start date for long-term analysis window.
        short_data (list[dict]): Recent price data (e.g., last year).
        long_data (list[dict]): Longer historical price data (e.g., last 3-5 years).
        short_vol (float): Annualized short-term volatility.
        long_vol (float): Annualized long-term volatility.
        filters (dict): Dictionary containing numeric thresholds for each momentum test.

    Returns:
        bool: True if the stock passes all momentum heuristic tests, False otherwise.
    """

    MA = {row["date"]: row["value"] for row in compute_sma(long_data, 200)}

    if not above_MA_test(long_data, MA, short_start, long_start, filters["percentageAboveMA"]):
        return False

    if not av_slope_test(MA, short_start, long_start, filters["avSlope"]):
        return False

    if not pos_returns_test(long_data, short_start, long_start, filters["posReturns"]):
        return False

    if not min_volatility_test(short_vol, long_vol, filters["minVolatilityMomentum"]):
        return False

    return True