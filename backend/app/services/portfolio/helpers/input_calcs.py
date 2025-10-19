import numpy as np
import pandas as pd

def compute_expected_returns(symbol_returns, decay=0.94):
    expected = {}
    for symbol, returns in symbol_returns.items():
        returns = np.array(returns, dtype=float)
        if len(returns) == 0:
            expected[symbol] = 0.0
            continue
        weights = np.array([(1 - decay) * decay**i for i in reversed(range(len(returns)))])
        weights /= weights.sum()
        expected[symbol] = float(np.sum(returns * weights))
    return expected

def compute_risk_matrix(symbol_returns):
    df = pd.DataFrame(symbol_returns)
    df = df.dropna(how="any")
    cov = df.cov().values
    symbols = df.columns.tolist()
    return {"symbols": symbols, "cov_matrix": cov.tolist()}