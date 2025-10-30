import os
import itertools
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
    A = np.vstack([x, np.ones_like(x)]).T
    beta, alpha = np.linalg.lstsq(A, y, rcond=None)[0]
    residuals = y - (alpha + beta * x)
    adf_result = adfuller(residuals)

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
    prices_np = {sym: df[sym].to_numpy() for sym in pair}
    dates = df.index.to_numpy()

    def get_aligned(s1, s2):
        x, y = prices_np[s1], prices_np[s2]
        mask = ~np.isnan(x) & ~np.isnan(y)
        return x[mask], y[mask]

    x, y = get_aligned(s1, s2)

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

def process_chunk(chunk, df, w_corr, w_coint):
    chunk_results = []
    for pair in chunk:
        res = process_pair(pair, df, w_corr, w_coint)
        if res:
            chunk_results.append(res)
    return chunk_results

# === 3. Main engine for parallel pair analysis ===
def analyze_pairs(
    symbols,
    prices_dict,
    w_corr=0.5,
    w_coint=0.5,
    max_workers=None,
    progress_callback=None,
    chunk_size=100  # number of pairs per process
):

    # Convert price dicts to aligned DataFrame
    df = pd.DataFrame({
        sym: pd.Series({p["date"]: p["close"] for p in prices_dict[sym]})
        for sym in symbols
    }).sort_index()

    pairs_list = list(itertools.combinations(symbols, 2))
    total_pairs = len(pairs_list)
    results = []

    if total_pairs == 0:
        return results

    if max_workers is None:
        max_workers = min(32, os.cpu_count() - 1 or 3)

    # --- Split pairs into chunks ---
    chunks = [pairs_list[i:i+chunk_size] for i in range(0, total_pairs, chunk_size)]

    done = 0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_chunk, chunk, df, w_corr, w_coint) for chunk in chunks]
        for future in as_completed(futures):
            chunk_result = future.result()
            results.extend(chunk_result)
            if progress_callback:
                done += len(chunk_result)
                progress_callback(done, total_pairs)

    # Final callback
    if progress_callback:
        progress_callback(total_pairs, total_pairs)

    return results