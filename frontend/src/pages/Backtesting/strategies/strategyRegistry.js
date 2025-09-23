export const strategies = {
  sma_crossover: {
    label: "Moving Average Crossover",
    params: [
      // --- Basic ---
      { name: "shortPeriod", label: "Short SMA Period", type: "number", default: 20, category: "basic" },
      { name: "longPeriod", label: "Long SMA Period", type: "number", default: 50, category: "basic" },

      // --- Advanced ---
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, category: "advanced" },
      { name: "maxConcurrentPositions", label: "Max Concurrent Positions", type: "number", default: 5, category: "advanced" },
    ],
  },

  bollinger_reversion: {
    label: "Bollinger Band Reversion",
    params: [
      // --- Basic ---
      { name: "period", label: "SMA Period", type: "number", default: 20, category: "basic" },
      { name: "stdDev", label: "Standard Deviations", type: "number", default: 2, category: "basic" },

      // --- Advanced ---
      { name: "bollingerMultiplier", label: "Band Multiplier", type: "number", default: 2, category: "advanced" },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, category: "advanced" },
    ],
  },

  rsi_reversion: {
    label: "RSI Mean Reversion",
    params: [
      // --- Basic ---
      { name: "period", label: "RSI Period", type: "number", default: 14, category: "basic" },
      { name: "oversold", label: "Oversold Threshold", type: "number", default: 30, category: "basic" },
      { name: "overbought", label: "Overbought Threshold", type: "number", default: 70, category: "basic" },

      // --- Advanced ---
      { name: "signalSmoothing", label: "Signal Smoothing (EMA)", type: "number", default: 3, category: "advanced" },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, category: "advanced" },
    ],
  },

  momentum: {
    label: "Time-Series Momentum",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 63, category: "basic" },

      // --- Advanced ---
      { name: "holdingPeriod", label: "Holding Period", type: "number", default: 21, category: "advanced" },
      { name: "volatilityTarget", label: "Volatility Target (%)", type: "number", default: 15, category: "advanced" },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, category: "advanced" },
    ],
  },

  breakout: {
    label: "Breakout Strategy",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 20, category: "basic" },

      // --- Advanced ---
      { name: "breakoutMultiplier", label: "Breakout Threshold Multiplier", type: "number", default: 1.0, category: "advanced" },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, category: "advanced" },
    ],
  },

  pairs_trading: {
    label: "Pairs Trading",
    params: [
      // --- Basic ---
      { name: "lookback", label: "Lookback Period", type: "number", default: 20, category: "basic" },
      { name: "entryZ", label: "Entry Z-Score", type: "number", default: 2, category: "basic" },
      { name: "exitZ", label: "Exit Z-Score", type: "number", default: 0.5, category: "basic" },

      // --- Advanced ---
      { name: "maxHolding", label: "Max Holding Days", type: "number", default: 20, category: "advanced" },
      { name: "hedgeRatio", label: "Hedge Ratio (β)", type: "number", default: 1.0, category: "advanced" },
      { name: "positionSizing", label: "Position Sizing (%)", type: "number", default: 100, category: "advanced" },
    ],
  },
};
