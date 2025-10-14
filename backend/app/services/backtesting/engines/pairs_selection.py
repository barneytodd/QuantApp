import pandas as pd
import numpy as np
from itertools import combinations
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

from ..helpers.pairs.align_series import align_series
from app.utils.scoring import compute_pair_score


# === 1. Engle-Granger test ===
def engle_granger_test(y, x):
    """Run Engle-Granger cointegration test."""
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    residuals = model.resid
    adf_result = adfuller(residuals)

    alpha = float(model.params.iloc[0])
    beta = float(model.params.iloc[1])

    return {
        "alpha": alpha,
        "beta": beta,
        "p_value": float(adf_result[1]),
        "cointegrated": adf_result[1] < 0.05,
    }


# === 2. Single pair processing ===
def process_pair(pair, df, w_corr, w_coint):
    """Compute correlation, cointegration and score for one pair."""
    s1, s2 = pair
    x, y = df[s1].dropna(), df[s2].dropna()
    x, y = x.align(y, join="inner")

    if len(x) < 2:
        return None

    corr = np.corrcoef(x, y)[0, 1]

    result = engle_granger_test(y, x)
    score = compute_pair_score(corr, result["p_value"], result["beta"], w_corr, w_coint)

    return {
        "stock1": s1,
        "stock2": s2,
        "corr": corr,
        "p_value": result["p_value"],
        "beta": result["beta"],
        "score": score,
    }


# === 3. Main parallel engine ===
def analyze_pairs(
    symbols,
    prices_dict,
    w_corr=0.5,
    w_coint=0.5,
    max_workers=None,
    progress_callback=None,
):
    """
    Compute correlation, cointegration & scores for all symbol pairs (parallel).
    Supports optional progress_callback(done, total).
    """
    df = pd.DataFrame({
        sym: pd.Series({p["date"]: p["close"] for p in prices_dict[sym]})
        for sym in symbols
    }).sort_index()

    pairs_list = list(combinations(symbols, 2))
    total_pairs = len(pairs_list)
    results = []

    if total_pairs == 0:
        return results

    if max_workers is None:
        max_workers = min(32, os.cpu_count() or 4)

    print(f"Analyzing {total_pairs} pairs with {max_workers} workers...")

    done = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_pair, pair, df, w_corr, w_coint)
            for pair in pairs_list
        ]

        for f in as_completed(futures):
            res = f.result()
            done += 1
            if res:
                results.append(res)

            # Update progress via callback
            if progress_callback:
                try:
                    progress_callback(done, total_pairs)
                except Exception:
                    pass  # avoid crashing if callback breaks

    # Final completion callback
    if progress_callback:
        try:
            progress_callback(total_pairs, total_pairs)
        except Exception:
            pass

    print("Pair analysis completed.")
    return results
