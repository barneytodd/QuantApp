# app/services/optimiser.py
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
from app.utils.data_helpers import convert_numpy
from ..helpers.optimisation.cross_validation import cross_val_score


# --- Parameter optimisation ---
def optimise_parameters(data, symbols, param_space, optim_params, initial_capital=10000):
    """
    data: dict {symbol: [{"date":..., "close":...}, ...]} - stores data separately for each symbol
    symbols: dict { symbol: strategy } - stores pairs as single symbols
    param_space: dict of strategy parameters
    optim_params: dict of optimisation parameters
    """
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
        score = cross_val_score(data, symbols, fixed_params, kwargs, optim_params, initial_capital)
        trials.append({"params": kwargs, "score": score})
        return -score  # maximize Sharpe -> minimize negative

    res = gp_minimize(objective, sk_space, n_calls=int(iterations), random_state=42)
    best_params = dict(zip(names, res.x))
    best_score = -res.fun

    best_basic_params = {k:v for k,v in best_params.items() if param_space[k]["category"] == "basic"}
    best_advanced_params = {k:v for k,v in best_params.items() if param_space[k]["category"] == "advanced"}
    print(best_basic_params)
    return convert_numpy({
        "best_basic_params": best_basic_params,
        "best_advanced_params": best_advanced_params,
        "best_score": float(best_score),
        "trials": trials,
    })
