from datetime import datetime
from dateutil.relativedelta import relativedelta


def prepare_backtest_inputs(payload):
    """
    Prepares common inputs for both standard and walk-forward backtests.

    Steps:
        1. Validates that symbols and parameters exist.
        2. Flattens all symbols into a single list.
        3. Creates a mapping of unique symbol-strategy keys to their metadata.
        4. Extracts lookback values and flattens parameter values.

    Args:
        payload: Backtest request payload with `symbolItems` and `params`.

    Returns:
        individual_symbols (list): flattened list of all symbols
        strategy_symbols (dict): mapping of unique keys to symbol-strategy info
        params (dict): flattened parameter values
        max_lookback (int): maximum lookback across all parameters
    """
    # Validate inputs
    if not payload.symbolItems:
        print("No symbol items in payload:", payload)
        raise ValueError("No symbols provided")
    if not payload.params:
        print("No params in payload:", payload)
        raise ValueError("No parameters provided")

    # --- Flatten all symbols across items ---
    individual_symbols = list({s for item in payload.symbolItems for s in item["symbols"]})

    # --- Build symbol-strategy mapping ---
    strategy_symbols = {}
    for item in payload.symbolItems:
        key_base = "-".join(item["symbols"])  # e.g., "AAPL" or "AAPL-MSFT"
        strategy = item["strategy"]
        key = f"{key_base}_{strategy}"  # unique key for each symbol-strategy combination
        strategy_symbols[key] = {
            "symbol": key_base,
            "strategy": strategy,
            "weight": item.get("weight", 1),  # default weight is 1
        }

    # --- Compute maximum lookback across all parameters ---
    max_lookback = max(
        (v["value"] for k, v in payload.params.items() if v.get("lookback")), default=0
    )

    # Flatten parameter values into a simple dict
    params = {p: v["value"] for p, v in payload.params.items()}

    return individual_symbols, strategy_symbols, params, max_lookback


def create_walkforward_windows(start_date: str, end_date: str, window_length: int):
    """
    Generate rolling walk-forward windows for backtesting.

    Args:
        start_date (str): start date of the data in "YYYY-MM-DD" format
        end_date (str): end date of the data in "YYYY-MM-DD" format
        window_length (int): length of each window in years

    Returns:
        List[dict]: each dict contains `start` and `end` of a window
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    windows = []

    current_start = start
    # Slide the window forward by 1 year at a time until reaching the end date
    while current_start + relativedelta(years=window_length) <= end + relativedelta(days=1):
        current_end = min(current_start + relativedelta(years=window_length), end)
        windows.append({
            "start": current_start.strftime("%Y-%m-%d"),
            "end": current_end.strftime("%Y-%m-%d"),
        })
        current_start += relativedelta(years=1)  # move window forward by 1 year

    return windows
