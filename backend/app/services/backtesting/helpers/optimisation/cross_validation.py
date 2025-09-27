from ...engines.backtest_engine import run_backtest
import numpy as np
from .data_processing import check_data, get_fold_data


# --- Walk-forward cross-validation ---
def cross_val_score(data, symbols, fixed_params, train_params, optim_params, initial_capital):
    """
    data: dict {symbol: [{"date":..., "close":...}, ...]} - stores data separately for each symbol
    symbols: dict { symbol: strategy } - stores pairs as single symbols
    fixed_params: dict of non-optimisable strategy parameters
    train_params: dict of optimisable strategy parameters
    optim_params: dict of optimisation parameters
    initial_capital: int
    """
    min_folds = optim_params["minCvFolds"]
    max_folds = optim_params["maxCvFolds"]
    fold_length = optim_params["foldLength"]
    
    check = check_data(data, fixed_params, min_folds, max_folds, fold_length)
    if not check["passed"]:
        raise ValueError(
            f"Not enough data for symbols. Must have {required_years} years prior to backtest start. Update data for {check['mdr']}"
        )

    num_folds = check["folds"]
    start_date = check["start_date"]
    end_date = check["end_date"]

    scores = []

    params = {**fixed_params, **train_params}
    for fold_idx in range(num_folds):
        fold_data = get_fold_data(data, fold_idx, fold_length, num_folds, end_date)
        fold_results = [result for result in run_backtest(fold_data, symbols, params) if result["symbol"] == "overall"][0]
        scores.append(fold_results["metrics"]["sharpe_ratio"])

    return float(np.mean(scores))