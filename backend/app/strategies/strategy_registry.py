from . import strategy_wrappers as sw

# Registry of available trading strategy backtest functions
strategies = {
    "sma_crossover": sw.backtest_sma,
    "bollinger_reversion": sw.backtest_bollinger,
    "rsi_reversion": sw.backtest_rsi,
    "momentum": sw.backtest_momentum,
    "breakout": sw.backtest_breakout,
    "pairs_trading": sw.backtest_pairs,
}
