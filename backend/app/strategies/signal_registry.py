from . import signal_generators as sg

# Strategy registry
generators = {
    "sma_crossover": sg.sma_signal_generator,
    "bollinger_reversion": sg.bollinger_signal_generator,
    "rsi_reversion": sg.rsi_signal_generator,
    "momentum": sg.momentum_signal_generator,
    "breakout": sg.breakout_signal_generator,
    "pairs_trading": sg.pairs_signal_generator,
}

def generate_signal(strategy_name, data, i, params):
    """
    Dispatches to the correct signal generator based on strategy name.

    Args:
        strategy_name (str): key in `generators` registry
        data (list[dict] or pd.DataFrame): price or OHLC data
        i (int): current index in data
        params (dict): parameters for the strategy

    Returns:
        str: trading signal ("buy", "sell", "hold", "long", "short", "exit")
    """
    generator = generators.get(strategy_name)
    if not generator:
        raise ValueError(f"Strategy '{strategy_name}' is not registered.")
    return generator(data, i, params)
