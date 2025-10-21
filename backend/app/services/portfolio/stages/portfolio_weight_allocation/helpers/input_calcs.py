import numpy as np
import pandas as pd

def compute_expected_returns(symbol_returns, decay=0.94):
    expected = {}
    for symbol, returns in symbol_returns.items():
        if returns is None:
            expected[symbol] = 0.0
            continue
        returns_array = np.array([r["return"] for r in returns], dtype=float)
        weights = np.array([(1 - decay) * decay**i for i in reversed(range(len(returns_array)))])
        weights /= weights.sum()
        expected[symbol] = float(np.sum(returns_array * weights))
    return expected

def compute_risk_matrix(symbol_returns):
    dfs = []
    for symbol, data in symbol_returns.items():
        # Convert list of dicts to DataFrame
        if not data:  # covers both None and empty list
            print(f" No data for {symbol}, skipping...")
            continue

        df = pd.DataFrame(data)
        if df.empty or "date" not in df or "return" not in df:
            print(f" Invalid or empty data for {symbol}, skipping...")
            continue

        df = df[["date", "return"]].set_index("date")
        df.rename(columns={"return": symbol}, inplace=True)
        dfs.append(df)

    # Merge all symbols by date
    df_all = pd.concat(dfs, axis=1).fillna(0)  # fill missing returns with 0

    # Compute covariance matrix
    cov = df_all.cov().values
    symbols = df_all.columns.tolist()

    return {"symbols": symbols, "cov_matrix": cov.tolist()}