import pandas as pd

def align_series(prices_dict, stock1, stock2):
    """
    Align two stock time series by date for pairs analysis.

    Args:
        prices_dict (dict): Dictionary of price series per symbol, e.g.
                            { "AAPL": [{"date": ..., "close": ...}, ...], ... }
        stock1 (str): First stock symbol
        stock2 (str): Second stock symbol

    Returns:
        pd.DataFrame: DataFrame with columns ["date", stock1, stock2"] containing
                      only dates present in both series.
    """

    # Convert raw price lists to DataFrames
    df1 = pd.DataFrame(prices_dict[stock1])
    df2 = pd.DataFrame(prices_dict[stock2])

    # Handle empty series
    if df1.empty or df2.empty:
        return pd.DataFrame(columns=["date", stock1, stock2])
    
    # Keep only 'date' and 'close', rename 'close' to the stock symbol
    df1 = df1[["date", "close"]].rename(columns={"close": stock1})
    df2 = df2[["date", "close"]].rename(columns={"close": stock2})

    # Merge on 'date' using inner join to retain only common dates
    merged = pd.merge(df1, df2, on="date", how="inner").sort_values("date")

    return merged
