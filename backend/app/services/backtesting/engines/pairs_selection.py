import os
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

from app.services.backtesting.helpers.pairs import compute_pair_score


# === 1. Engle-Granger cointegration test ===
def engle_granger_test(y, x):
    """
    Run Engle-Granger two-step cointegration test.
    
    Args:
        y (pd.Series): Dependent variable series
        x (pd.Series): Independent variable series

    Returns:
        dict: {
            alpha: intercept,
            beta: slope,
            p_value: ADF p-value on residuals,
            cointegrated: True if p < 0.05
        }
    """
    x = sm.add_constant(x)  # add intercept
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


# === 2. Process a single pair ===
def process_pair(pair, df, w_corr, w_coint):
    """
    Compute correlation, Engle-Granger cointegration, and score for a single pair.

    Args:
        pair (tuple): (symbol1, symbol2)
        df (pd.DataFrame): DataFrame with columns = symbols, index = dates
        w_corr (float): weight for correlation
        w_coint (float): weight for cointegration

    Returns:
        dict | None: metrics for the pair or None if insufficient data
    """
    s1, s2 = pair
    x, y = df[s1].dropna(), df[s2].dropna()
    x, y = x.align(y, join="inner")  # keep only overlapping dates

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


# === 3. Main engine for parallel pair analysis ===
def analyze_pairs(
    symbols,
    prices_dict,
    w_corr=0.5,
    w_coint=0.5,
    max_workers=None,
    progress_callback=None,
):
    """
    Compute correlation, cointegration, and scores for all symbol pairs in parallel.

    Args:
        symbols (list[str]): list of symbols
        prices_dict (dict): symbol -> list of OHLCV dicts
        w_corr (float): correlation weight
        w_coint (float): cointegration weight
        max_workers (int): number of parallel workers
        progress_callback (callable): function(done, total)

    Returns:
        list[dict]: analysis results for all pairs
    """
    # Convert price dicts into DataFrame
    df = pd.DataFrame({
        sym: pd.Series({p["date"]: p["close"] for p in prices_dict[sym] if sym in prices_dict.keys()})
        for sym in symbols
    }).sort_index()
   
    pairs_list = list(combinations(symbols, 2))
    total_pairs = len(pairs_list)
    results = []

    if total_pairs == 0:
        return results

    if max_workers is None:
        max_workers = min(32, os.cpu_count() - 1 or 3)

    print(f"Analyzing {total_pairs} pairs with {max_workers} workers...")

    done = 0

    # Parallel processing of all pairs
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

            if progress_callback:
                try:
                    progress_callback(done, total_pairs)
                except Exception:
                    pass

    # Final callback indicating completion
    if progress_callback:
        try:
            progress_callback(total_pairs, total_pairs)
        except Exception:
            pass

    print("Pair analysis completed.")
    return results
