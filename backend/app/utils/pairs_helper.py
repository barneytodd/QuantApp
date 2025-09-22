import pandas as pd

def align_series(prices_dict, stock1, stock2):
    """
    prices_dict: {symbol: [{"date": "...", "close": ...}, ...]}
    stock1, stock2: strings
    """
    df1 = pd.DataFrame(prices_dict[stock1])
    df2 = pd.DataFrame(prices_dict[stock2])
    print(df1.head())
    # Keep only date + close
    df1 = df1[["date", "close"]].rename(columns={"close": stock1})
    df2 = df2[["date", "close"]].rename(columns={"close": stock2})

    # Merge on date (inner join so only common dates remain)
    merged = pd.merge(df1, df2, on="date", how="inner").sort_values("date")

    return merged