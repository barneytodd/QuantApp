import pandas as pd

def prepare_price_matrix(data: dict, symbols: dict):
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

    for sym_info in symbols.values():
        syms = sym_info["symbols"]
        for sym in syms:
            if sym not in price_matrix.columns:
                price_matrix[sym] = 0

    price_matrix.index = pd.to_datetime(price_matrix.index)
    numeric_cols = price_matrix.select_dtypes(include='number').columns
    
    non_numeric_cols = price_matrix.select_dtypes(exclude='number').columns
    price_matrix[non_numeric_cols] = 0
    
    price_matrix[numeric_cols] = price_matrix[numeric_cols].sort_index().ffill().bfill().fillna(0)
    return price_matrix
