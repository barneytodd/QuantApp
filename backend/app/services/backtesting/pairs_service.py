import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from itertools import combinations
from app.utils.scoring import compute_pair_score
import numpy as np
import pandas as pd
from app.utils.pairs_helpers import align_series

def engle_granger_test(y, x):
    """Run Engle-Granger cointegration test."""
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    residuals = model.resid
    adf_result = adfuller(residuals)

    return {
        "alpha": float(model.params[0]),
        "beta": float(model.params[1]),
        "p_value": float(adf_result[1]),
        "cointegrated": adf_result[1] < 0.05
    }

def analyze_pairs(symbols, prices, w_corr=0.5, w_coint=0.5):
    """
    Compute correlation, cointegration & scores for all symbol pairs.
    """
    pairs = []
    for s1, s2 in combinations(symbols, 2):
        data = align_series(prices, s1, s2)
        x, y = data[s1].values, data[s2].values
        if len(x) > 0 and len(y) > 0:
            corr = np.corrcoef(x, y)[0, 1]
        else:
            corr = np.nan

        corr = np.corrcoef(y, x)[0, 1]
        result = engle_granger_test(y, x)

        score = compute_pair_score(corr, result["p_value"], result["beta"], w_corr, w_coint)

        pairs.append({
            "stock1": s1,
            "stock2": s2,
            "corr": corr,
            "p_value": result["p_value"],
            "beta": result["beta"],
            "score": score
        })
    return pairs
