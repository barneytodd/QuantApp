import { backtestSMA, backtestBollinger, backtestRSI, backtestMomentum, backtestBreakout, backtestPairs } from "./strategyWrappers";
// import more strategies here...

// registry of strategies
export const strategies = {
  "sma_crossover": {
    label: "Moving Average Crossover",
    run: backtestSMA,
    params: [
      { name: "shortPeriod", label: "Short SMA Period", type: "number", default: 20 },
      { name: "longPeriod", label: "Long SMA Period", type: "number", default: 50 },
    ],
  },

  "bollinger_reversion": {
    label: "Bollinger Band Reversion",
    run: backtestBollinger,
    params: [
      { name: "period", label: "SMA Period", type: "number", default: 20 },
      { name: "stdDev", label: "Standard Deviations", type: "number", default: 2 },
    ],
  },

  "rsi_reversion": {
    label: "RSI Mean Reversion",
    run: backtestRSI,
    params: [
      { name: "period", label: "RSI Period", type: "number", default: 14 },
      { name: "oversold", label: "Oversold Threshold", type: "number", default: 30 },
      { name: "overbought", label: "Overbought Threshold", type: "number", default: 70 },
    ],
  },

  "momentum": {
    label: "Time-Series Momentum",
    run: backtestMomentum,
    params: [
      { name: "lookback", label: "Lookback Period", type: "number", default: 63 }, // ~3 months
    ],
  },

  "breakout": {
    label: "Breakout Strategy",
    run: backtestBreakout,
    params: [
      { name: "lookback", label: "Lookback Period", type: "number", default: 20 }, // ~1 month
    ],
  },

  pairs_trading: {
    label: "Pairs Trading",
    run: backtestPairs,
    params: [
      { name: "symbol1", label: "Symbol 1", type: "text", default: "AAPL" },
      { name: "symbol2", label: "Symbol 2", type: "text", default: "MSFT" },
      { name: "lookback", label: "Lookback Period", type: "number", default: 20 },
      { name: "entryZ", label: "Entry Z-Score", type: "number", default: 2 },
      { name: "exitZ", label: "Exit Z-Score", type: "number", default: 0.5 },
    ],
  },

};
