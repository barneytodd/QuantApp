from app.services.backtesting.engines.backtest_engine import run_backtest
from app.services.backtesting.engines.pairs_backtest_engine import run_pairs_backtest
from app.strategies.signal_generators import (
    sma_signal_generator, bollinger_signal_generator, rsi_signal_generator,
    momentum_signal_generator, breakout_signal_generator
)

# Wrapper functions for different trading strategies
def backtest_sma(data, params, initial_capital):
    return run_backtest(data, params, sma_signal_generator, initial_capital)

def backtest_bollinger(data, params, initial_capital):
    return run_backtest(data, params, bollinger_signal_generator, initial_capital)

def backtest_rsi(data, params, initial_capital):
    return run_backtest(data, params, rsi_signal_generator, initial_capital)

def backtest_momentum(data, params, initial_capital):
    return run_backtest(data, params, momentum_signal_generator, initial_capital)

def backtest_breakout(data, params, initial_capital):
    return run_backtest(data, params, breakout_signal_generator, initial_capital)

def backtest_pairs(data, params, stock1, stock2, initial_capital):
    return run_pairs_backtest(data, params, stock1, stock2, initial_capital)
