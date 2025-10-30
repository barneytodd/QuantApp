import pandas as pd

def prepare_price_matrix(data: dict):
    """
    Converts dict of OHLC lists into a single DataFrame of close prices
    with dates as index and symbols as columns.
    
    Args:
        data (dict): {symbol: [{"date":..., "close":...}, ...]}
    
    Returns:
        pd.DataFrame: index = dates, columns = symbols
    """
    price_matrix = pd.DataFrame({
        symbol: pd.Series({row['date']: row['close'] for row in rows})
        for symbol, rows in data.items()
    })
    price_matrix.index = pd.to_datetime(price_matrix.index)
    numeric_cols = price_matrix.select_dtypes(include='number').columns
    price_matrix[numeric_cols] = price_matrix[numeric_cols].sort_index().ffill().bfill()
    return price_matrix
