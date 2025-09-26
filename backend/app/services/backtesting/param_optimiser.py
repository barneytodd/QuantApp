# app/services/optimiser.py
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
import numpy as np
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from .engines.backtest_engine import run_backtest, combine_results
from app.utils.data_helpers import fetch_price_data, convert_numpy
from sqlalchemy.orm import Session
from fastapi import Depends
from app.strategies.strategy_registry import strategies

# --- Check if symbols have enough historical data ---
def check_data(symbols, params, min_folds, max_folds, required_years, db):
    data = {}
    result = True
    more_data_required = []
    param_start_date = date.fromisoformat(params["startDate"])

    start_date_candidate = param_start_date - relativedelta(years=max_folds + required_years)
    end_date = param_start_date - datetime.timedelta(days=1)

    max_start_date = param_start_date - relativedelta(years=required_years)

    for symbol in symbols:
        symbol_data = fetch_price_data(db, symbol, end=end_date)
        if not symbol_data:
            more_data_required.append(symbol)
            result = False
            continue

        data[symbol] = symbol_data
        first_date = date.fromisoformat(symbol_data[0]["date"])
        last_date = date.fromisoformat(symbol_data[-1]["date"])

        # Check if symbol covers required years
        if first_date > max_start_date or last_date < end_date:
            more_data_required.append(symbol)
            result = False

        # Adjust fold start if earliest date is later
        if first_date > start_date_candidate:
            start_date_candidate = first_date

    # Determine number of folds possible
    total_years_available = (end_date - start_date_candidate).days // 365
    num_folds = min(max_folds, total_years_available - required_years + min_folds)
    num_folds = max(1, num_folds)  # ensure at least 1 fold

    return {"passed": result, "mdr": more_data_required, "data": data, "folds": num_folds, "start_date": start_date_candidate, "end_date": end_date}

def get_fold_data(symbol_data, fold_idx, train_years, test_years, num_folds, end_date):
    # calculate dates for this fold
    years_before_end = num_folds + train_years + test_years - 1 - fold_idx
    train_start = end_date - datetime.timedelta(days=365*years_before_end)
    train_end = train_start + datetime.timedelta(days=365*train_years - 1)
    test_start = train_end + datetime.timedelta(days=1)
    test_end = test_start + datetime.timedelta(days=365*test_years - 1)
    
    # slice data
    train_data = {sym: [d for d in data if train_start <= date.fromisoformat(d["date"]) <= train_end] for sym, data in symbol_data.items()}
    test_data  = {sym: [d for d in data if test_start <= date.fromisoformat(d["date"]) <= test_end] for sym, data in symbol_data.items()}
    
    return train_data, test_data


# --- Walk-forward cross-validation ---
def cross_val_score(strategy, symbols, fixed_params, train_params, optim_params, initial_capital, db):
    min_folds = optim_params["minCvFolds"]
    max_folds = optim_params["maxCvFolds"]
    train_years = optim_params["trainYears"]
    test_years = optim_params["testYears"]

    required_years = train_years + test_years + min_folds - 1
    check = check_data(symbols, fixed_params, min_folds, max_folds, required_years, db)
    if not check["passed"]:
        raise ValueError(
            f"Not enough data for symbols. Must have {required_years} years prior to backtest start. Update data for {check['mdr']}"
        )

    data = check["data"]
    num_folds = check["folds"]
    start_date = check["start_date"]
    end_date = check["end_date"]

    scores = []

    params = {**fixed_params, **train_params}
    print(params)

    for fold_idx in range(num_folds):
        train_data, _ = get_fold_data(data, fold_idx, train_years, test_years, num_folds, end_date)
        fold_results = [strategies[strategy](data, params, initial_capital / len(symbols)) for data in train_data.values()]
        combined = combine_results(fold_results)
        scores.append(combined["metrics"]["sharpe_ratio"])


    return float(np.mean(scores))


# --- Parameter optimisation ---
def optimise_parameters(strategy, symbols, param_space, optim_params, db, initial_capital=10000):
    sk_space = []
    names = []
    iterations = optim_params["iterations"]

    fixed_params = {p:v["value"] for p,v in param_space.items() if not v["optimise"]}
    train_params = {p:v for p,v in param_space.items() if v["optimise"]}

    # Build skopt search space
    for name, param in train_params.items():
        names.append(name)
        if param["type"] == "number":
            if param["integer"]:
                sk_space.append(Integer(param["bounds"][0], param["bounds"][1], name=name))
            else:
                sk_space.append(Real(param["bounds"][0], param["bounds"][1], name=name))
        elif param["type"] == "categorical":
            sk_space.append(Categorical(param["options"], name=name))

    trials = []

    @use_named_args(sk_space)
    def objective(**kwargs):
        score = cross_val_score(strategy, symbols, fixed_params, kwargs, optim_params, initial_capital, db)
        trials.append({"params": kwargs, "score": score})
        return -score  # maximize Sharpe -> minimize negative

    res = gp_minimize(objective, sk_space, n_calls=int(iterations), random_state=42)
    best_params = dict(zip(names, res.x))
    best_score = -res.fun

    test_scores = []

    #test_results = [strategies[strategy](data, best_params, initial_capital) 
    #                for data in test_data.values()]
    #combined_test = combine_results(test_results)
    #test_scores.append(combined_test["metrics"]["sharpe_ratio"])

    best_basic_params = {k:v for k,v in best_params.items() if param_space[k]["category"] == "basic"}
    best_advanced_params = {k:v for k,v in best_params.items() if param_space[k]["category"] == "advanced"}
    

    return convert_numpy({
        "best_basic_params": best_basic_params,
        "best_advanced_params": best_advanced_params,
        "best_score": float(best_score),
        "trials": trials,
        "test_score": float(np.mean(test_scores)) if test_scores else None
    })
