import numpy as np
import pandas as pd

# === Expected Returns & Risk Matrix Computation Engine ===

def compute_expected_returns(symbol_returns: dict, decay: float = 0.94) -> dict:
    """
    Compute exponentially weighted expected returns for each symbol.
    
    Args:
        symbol_returns: dict mapping symbol -> list of dicts with 'date' and 'return'
        decay: float, exponential decay factor (default 0.94)
    
    Returns:
        dict mapping symbol -> expected return (float)
    """
    expected = {}

    for symbol, returns in symbol_returns.items():
        # --- Handle missing or None returns ---
        if not returns:
            expected[symbol] = 0.0
            continue

        # --- Convert returns to NumPy array ---
        returns_array = np.array([r["return"] for r in returns], dtype=float)

        # --- Compute exponentially decaying weights ---
        weights = np.array([(1 - decay) * decay**i for i in reversed(range(len(returns_array)))])
        weights /= weights.sum()

        # --- Compute expected return ---
        expected[symbol] = float(np.sum(returns_array * weights))

    return expected


def compute_risk_matrix(symbol_returns: dict) -> dict:
    """
    Compute the covariance matrix of returns across all symbols.

    Args:
        symbol_returns: dict mapping symbol -> list of dicts with 'date' and 'return'

    Returns:
        dict with:
            symbols: list of symbols included
            cov_matrix: covariance matrix as a nested list
    """
    dfs = []

    for symbol, data in symbol_returns.items():
        # --- Skip missing or empty data ---
        if not data:
            print(f"No data for {symbol}, skipping...")
            continue

        # --- Convert list of dicts to DataFrame ---
        df = pd.DataFrame(data)
        if df.empty or "date" not in df or "return" not in df:
            print(f"Invalid or empty data for {symbol}, skipping...")
            continue

        df = df[["date", "return"]].set_index("date")
        df.rename(columns={"return": symbol}, inplace=True)
        dfs.append(df)

    # --- Merge all symbols by date, filling missing returns with 0 ---
    df_all = pd.concat(dfs, axis=1).fillna(0)

    # --- Compute covariance matrix ---
    cov = df_all.cov().values
    symbols = df_all.columns.tolist()

    return {"symbols": symbols, "cov_matrix": cov.tolist()}
