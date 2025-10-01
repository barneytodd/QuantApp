export const strategies = {
  sma_crossover: {
    label: "Moving Average Crossover",
    params: [
      // --- Basic ---
      { name: "shortPeriod", label: "Short SMA Period", type: "number", default: 20, bounds: [5, 30], category: "basic", optimise: true, integer: true },
      { name: "longPeriod", label: "Long SMA Period", type: "number", default: 50, bounds: [20, 200], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
    ],
  },

  bollinger_reversion: {
    label: "Bollinger Band Reversion",
    params: [
      // --- Basic ---
      { name: "period", label: "SMA Period", type: "number", default: 20, bounds: [5,100], category: "basic", optimise: true, integer: true },
      { name: "bandMultiplier", label: "Band Multiplier", type: "number", default: 2, bounds: [1, 3], category: "basic", optimise: true, integer: false },
      
      // --- Advanced ---
    ],
  },

  rsi_reversion: {
    label: "RSI Mean Reversion",
    params: [
      // --- Basic ---
      { name: "period", label: "RSI Period", type: "number", default: 14, bounds: [5, 50], category: "basic", optimise: true, integer: true },
      { name: "oversold", label: "Oversold Threshold", type: "number", default: 30, bounds: [0, 50], category: "basic", optimise: true, integer: true },
      { name: "overbought", label: "Overbought Threshold", type: "number", default: 70, bounds: [50, 100], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
      { name: "signalSmoothing", label: "Signal Smoothing (EMA)", type: "categorical", default: 3, bounds: [1,2,3,5,8], category: "advanced", optimise: true },
    ],
  },

  momentum: {
    label: "Time-Series Momentum",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 63, bounds: [10, 250], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
      { name: "volTarget", label: "Volatility Target (%)", type: "categorical", default: 15, options: [5,10,15,20], category: "advanced", optimise: true },
      { name: "volLookback", label: "Volatility Lookback Period", type: "categorical", default: 20, options: [20, 60, 120, 252], category: "advanced", optimise: true },
      { name: "rebalanceFrequency", label: "Rebalance Frequency (days)", type: "categorical", default: 0, options: [0, 1, 5, 10, 20, 60, "onSignal"], category: "advanced", optimise: true, integer: true }
    ],
  },

  breakout: {
    label: "Breakout Strategy", 
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 20, bounds: [5, 100], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
      { name: "breakoutMultiplier", label: "Breakout Threshold Multiplier", type: "number", default: 0.0, bounds: [0.0, 0.5], category: "advanced", optimise: true, integer: false },
    ],
  },

  pairs_trading: {
    label: "Pairs Trading",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 20, bounds: [20, 200], category: "basic", optimise: true, integer: true },
      { name: "entryZ", label: "Entry Z-Score", type: "number", default: 2, bounds: [0.5, 5], category: "basic", optimise: true, integer: false },
      { name: "exitZ", label: "Exit Z-Score", type: "number", default: 0.5, bounds: [0, 3], category: "basic", optimise: true, integer: false },

      // --- Advanced ---
      { name: "maxHolding", label: "Max Holding Days", type: "number", default: 20, bounds: [1, 60], category: "advanced", optimise: true, integer: true },
      { name: "hedgeRatio", label: "Hedge Ratio (β)", type: "number", default: 1.0, bounds: [0.1, 2.0], category: "advanced", optimise: true, integer: false },
    ],
  },

  custom: {
    label: "Custom",
    params:[],
  },
};
