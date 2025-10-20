import pandas as pd
import numpy as np
import cvxpy as cp

def optimise_portfolio(mu_dict, cov_dict, w_baseline_dict, risk_aversion=0.5, baseline_reg=0.1, min_weight=0.0, max_weight=0.1, cleanup_threshold=1e-4):
    symbols = cov_dict["symbols"]
    cov_matrix = np.array(cov_dict["cov_matrix"])

    # Convert inputs to numpy arrays
    mu = np.array([mu_dict[s] for s in symbols])
    w_baseline = np.array([w_baseline_dict[s] for s in symbols])

    n = len(symbols)
    w = cp.Variable(n)

    # Objective: maximize mu^T w - lambda w^T Sigma w - gamma ||w - w_baseline||^2
    ret_term = mu.T @ w
    risk_term = risk_aversion * cp.quad_form(w, cov_matrix)
    baseline_penalty = baseline_reg * cp.sum_squares(w - w_baseline)
    
    objective = cp.Maximize(ret_term - risk_term - baseline_penalty)

    # Constraints: sum-to-one, long-only, max weight
    constraints = [
        cp.sum(w) == 1,
        w >= min_weight,
        w <= max_weight
    ]

    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.SCS)  # you can change solver if preferred
    
    # Convert result to Series
    weights = pd.Series(w.value, index=symbols, dtype=float)

    # === Post-processing cleanup ===
    weights[weights < 0] = np.maximum(weights[weights < 0], 0)  # clip negatives to 0
    weights[weights.abs() < cleanup_threshold] = 0              # zero out tiny numbers

    total = weights.sum()
    if total > 0:
        weights /= total  # renormalize to sum to 1

    # Optionally remove 0-weight assets
    weights = weights[weights > 0]

    return weights.to_dict()