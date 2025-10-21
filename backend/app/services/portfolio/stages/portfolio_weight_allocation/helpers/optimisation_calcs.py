import cvxpy as cp
import numpy as np
import pandas as pd

# === Constrained Portfolio Optimisation Engine ===

def optimise_portfolio(
    mu_dict: dict,
    cov_dict: dict,
    w_baseline_dict: dict,
    risk_aversion: float = 0.5,
    baseline_reg: float = 0.1,
    min_weight: float = 0.0,
    max_weight: float = 0.1,
    cleanup_threshold: float = 1e-4
) -> dict:
    """
    Solve a constrained portfolio optimisation problem using mean-variance with
    baseline deviation penalty.

    Objective:
        Maximise expected return minus risk minus deviation from baseline:
        max w^T mu - lambda * w^T Sigma w - gamma * ||w - w_baseline||^2

    Constraints:
        - Sum of weights == 1
        - Long-only (weights >= min_weight)
        - Maximum weight per asset <= max_weight

    Args:
        mu_dict: dict mapping symbol -> expected return
        cov_dict: dict with keys:
            symbols: list of symbols
            cov_matrix: nested list of covariance values
        w_baseline_dict: dict mapping symbol -> baseline weight
        risk_aversion: lambda, penalty on portfolio variance
        baseline_reg: gamma, penalty for deviation from baseline
        min_weight: minimum weight per asset
        max_weight: maximum weight per asset
        cleanup_threshold: small weights below this are zeroed

    Returns:
        dict mapping symbol -> optimized weight (non-zero only)
    """
    symbols = cov_dict["symbols"]
    cov_matrix = np.array(cov_dict["cov_matrix"])

    # --- Convert inputs to NumPy arrays ---
    mu = np.array([mu_dict[s] for s in symbols])
    w_baseline = np.array([w_baseline_dict[s] for s in symbols])
    n = len(symbols)

    # --- Define optimisation variable ---
    w = cp.Variable(n)

    # --- Define objective ---
    ret_term = mu.T @ w
    risk_term = risk_aversion * cp.quad_form(w, cov_matrix)
    baseline_penalty = baseline_reg * cp.sum_squares(w - w_baseline)
    objective = cp.Maximize(ret_term - risk_term - baseline_penalty)

    # --- Define constraints ---
    constraints = [
        cp.sum(w) == 1,   # weights sum to 1
        w >= min_weight,  # long-only lower bound
        w <= max_weight   # max weight per asset
    ]

    # --- Solve optimisation problem ---
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.SCS)

    # --- Convert solution to pandas Series ---
    weights = pd.Series(w.value, index=symbols, dtype=float)

    # --- Post-processing cleanup ---
    weights[weights < 0] = np.maximum(weights[weights < 0], 0)  # clip negatives
    weights[weights.abs() < cleanup_threshold] = 0              # zero tiny weights

    # --- Renormalise to sum to 1 ---
    total = weights.sum()
    if total > 0:
        weights /= total

    # --- Optionally remove zero-weight assets ---
    weights = weights[weights > 0]

    return weights.to_dict()
