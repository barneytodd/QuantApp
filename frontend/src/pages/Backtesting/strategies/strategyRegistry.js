export const strategies = {
  sma_crossover: {
    label: "Moving Average Crossover",
    params: [
      // --- Basic ---
      { name: "shortPeriod", label: "Short SMA Period", type: "number", default: 20, bounds: [5, 100], category: "basic", optimise: true, integer: true },
      { name: "longPeriod", label: "Long SMA Period", type: "number", default: 50, bounds: [20, 200], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, bounds: [1, 100], category: "advanced", optimise: true, integer: false },
      { name: "maxConcurrentPositions", label: "Max Concurrent Positions", type: "number", default: 5, bounds: [1, 20], category: "advanced", optimise: true, integer: true },
    ],
  },

  bollinger_reversion: {
    label: "Bollinger Band Reversion",
    params: [
      // --- Basic ---
      { name: "period", label: "SMA Period", type: "number", default: 20, bounds: [5, 100], category: "basic", optimise: true, integer: true },
      { name: "stdDev", label: "Standard Deviations", type: "number", default: 2, bounds: [0.5, 5], category: "basic", optimise: true, integer: false },

      // --- Advanced ---
      { name: "bollingerMultiplier", label: "Band Multiplier", type: "number", default: 2, bounds: [0.5, 5], category: "advanced", optimise: true, integer: false },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, bounds: [1, 100], category: "advanced", optimise: true, integer: false },
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
      { name: "signalSmoothing", label: "Signal Smoothing (EMA)", type: "number", default: 3, bounds: [1, 10], category: "advanced", optimise: true, integer: true },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, bounds: [1, 100], category: "advanced", optimise: true, integer: false },
    ],
  },

  momentum: {
    label: "Time-Series Momentum",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 63, bounds: [10, 250], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
      { name: "holdingPeriod", label: "Holding Period", type: "number", default: 21, bounds: [1, 60], category: "advanced", optimise: true, integer: true },
      { name: "volatilityTarget", label: "Volatility Target (%)", type: "number", default: 15, bounds: [1, 50], category: "advanced", optimise: true, integer: false },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, bounds: [1, 100], category: "advanced", optimise: true, integer: false },
    ],
  },

  breakout: {
    label: "Breakout Strategy",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 20, bounds: [5, 100], category: "basic", optimise: true, integer: true },

      // --- Advanced ---
      { name: "breakoutMultiplier", label: "Breakout Threshold Multiplier", type: "number", default: 1.0, bounds: [0.5, 5.0], category: "advanced", optimise: true, integer: false },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, bounds: [1, 100], category: "advanced", optimise: true, integer: false },
    ],
  },

  pairs_trading: {
    label: "Pairs Trading",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 20, bounds: [5, 100], category: "basic", optimise: true, integer: true },
      { name: "entryZ", label: "Entry Z-Score", type: "number", default: 2, bounds: [0.5, 5], category: "basic", optimise: true, integer: false },
      { name: "exitZ", label: "Exit Z-Score", type: "number", default: 0.5, bounds: [0, 3], category: "basic", optimise: true, integer: false },

      // --- Advanced ---
      { name: "maxHolding", label: "Max Holding Days", type: "number", default: 20, bounds: [1, 60], category: "advanced", optimise: true, integer: true },
      { name: "hedgeRatio", label: "Hedge Ratio (β)", type: "number", default: 1.0, bounds: [0.1, 2.0], category: "advanced", optimise: true, integer: false },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, bounds: [1, 100], category: "advanced", optimise: true, integer: false },
    ],
  },
};
