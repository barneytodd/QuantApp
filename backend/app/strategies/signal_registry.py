from . import signal_generators as sg

# Registry of available trading strategy backtest functions
generators = {
    "sma_crossover": sg.sma_signal_generator,
    "bollinger_reversion": sg.bollinger_signal_generator,
    "rsi_reversion": sg.rsi_signal_generator,
    "momentum": sg.momentum_signal_generator,
    "breakout": sg.breakout_signal_generator,
    "pairs_trading": sg.pairs_signal_generator,
}
