import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

# --- Check if symbols have enough historical data ---
def check_data(data, params, min_folds, max_folds, fold_length):
    """
    data: dict {symbol: [{"date":..., "close":...}, ...]} - end date already set
    params: dict of strategy parameters
    min_folds: int - minimum required number of folds
    max_folds: int - maximum number of folds to use
    fold_length: int - number of years of data in each fold
    """
    result = True
    more_data_required = []
    required_years = min_folds + fold_length - 1
    param_start_date = date.fromisoformat(params["startDate"])

    start_date_candidate = param_start_date - relativedelta(years=max_folds + required_years)
    end_date = param_start_date - datetime.timedelta(days=1)

    max_start_date = param_start_date - relativedelta(years=required_years)
    
    for symbol, symbol_data in data.items():
        if not symbol_data:
            more_data_required.append(symbol)
            result = False
            continue

        first_date = date.fromisoformat(symbol_data[0]["date"])
        last_date = date.fromisoformat(symbol_data[-1]["date"])

        # Check if symbol covers required years
        if first_date > max_start_date or last_date < end_date:
            more_data_required.append(symbol)
            result = False

        # Adjust fold start if earliest date is later
        elif first_date > start_date_candidate:
            start_date_candidate = first_date

    # Determine number of folds possible
    total_years_available = (end_date - start_date_candidate).days // 365
    num_folds = min(max_folds, total_years_available - fold_length + 1)
    num_folds = max(1, num_folds)  # ensure at least 1 fold

    return {"passed": result, "mdr": more_data_required, "folds": num_folds, "start_date": start_date_candidate, "end_date": end_date}


def get_fold_data(data, fold_idx, fold_length, num_folds, end_date):
    """
    data: dict {symbol: [{"date":..., "close":...}, ...]} - end date already set
    fold_idx: int in range(num_folds)
    fold_length: int - number of years of data in each fold
    num_folds: int - total number of folds
    end_date: date for end of training
    """
    # calculate dates for this fold
    years_before_end = num_folds + fold_length - 1 - fold_idx
    fold_start = end_date - datetime.timedelta(days=365*years_before_end)
    fold_end = fold_start + datetime.timedelta(days=365*fold_length - 1)
    
    # slice data
    fold_data = {sym: [d for d in sym_data if fold_start <= date.fromisoformat(d["date"]) <= fold_end] for sym, sym_data in data.items()}
    
    return fold_data