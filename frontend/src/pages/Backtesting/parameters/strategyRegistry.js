export const strategies = {
  sma_crossover: {
    label: "Moving Average Crossover",
    type: "momentum",
    params: [
      // --- Basic ---
      { 
        name: "shortPeriod", 
        label: "Short SMA Period", 
        type: "number", 
        default: 20, 
        bounds: [5, 30], 
        category: "basic", 
        optimise: true, 
        integer: true, 
        lookback: true,
        info: "Lookback period for short SMA \nRequired: int < Long SMA Period \nSuggested bounds [5,30]"
      },
      { 
        name: "longPeriod", 
        label: "Long SMA Period", 
        type: "number", 
        default: 50, 
        bounds: [20, 200], 
        category: "basic", 
        optimise: true, 
        integer: true,
        lookback: true,
        info: "Lookback period for long SMA \nRequired: int > Short SMA Period \nSuggested bounds [20,200]"
      },

      // --- Advanced ---
    ],
  },

  bollinger_reversion: {
    label: "Bollinger Band Reversion",
    type: "meanReversion",
    params: [
      // --- Basic ---
      { 
        name: "period", 
        label: "Lookback Period", 
        type: "number", 
        default: 20, 
        bounds: [5,100], 
        category: "basic", 
        optimise: true, 
        integer: true, 
        lookback: true,
        info: "Lookback period for calculating SMA and std \nRequired: int \nSuggested bounds [5,100]"
      },
      { name: "bandMultiplier", 
        label: "Band Multiplier", 
        type: "number", 
        default: 2, 
        bounds: [1, 3], 
        category: "basic", 
        optimise: true, 
        integer: false, 
        lookback: false,
        info: "Std multiplier to control band width \nSuggested bounds [1,3]"
      },
      
      // --- Advanced ---
    ],
  },

  rsi_reversion: {
    label: "RSI Mean Reversion",
    type: "meanReversion",
    params: [
      // --- Basic ---
      { 
        name: "period", 
        label: "RSI Period", 
        type: "number", 
        default: 14, 
        bounds: [5, 50], 
        category: "basic", 
        optimise: true, 
        integer: true,
        lookback: true,
        info: "Lookback period to calculate SMA \nRequired: int \nSuggested bounds [5,50]" 
      },
      { name: "oversold", 
        label: "Oversold Threshold", 
        type: "number", 
        default: 30, 
        bounds: [0, 50], 
        category: "basic", 
        optimise: true, 
        integer: true, 
        lookback: false,
        info: "RSI value below which asset is oversold \nRequired: int < Overbought Threshold \nSuggested bounds [0,50]"
      },
      { 
        name: "overbought", 
        label: "Overbought Threshold", 
        type: "number", 
        default: 70, 
        bounds: [50, 100], 
        category: "basic", 
        optimise: true, 
        integer: true, 
        lookback: false,
        info: "RSI value above which asset is oversold \nRequired: int > Oversold Threshold \nSuggested bounds [50,100]"
      },

      // --- Advanced ---
      { 
        name: "signalSmoothing", 
        label: "Signal Smoothing (EMA)", 
        type: "categorical", 
        default: 3, 
        bounds: [1,2,3,5,8], 
        category: "advanced", 
        optimise: true,
        integer: true,
        lookback: true,
        group: "Signal Smoothing",
        info: "Lookback period for EMA applied to RSI values \nRequired: int > 0 \nSet to 1 to remove smoothing \nSuggested bounds [1,8]"
      },
    ],
  },

  momentum: {
    label: "Time-Series Momentum",
    type: "momentum",
    params: [
      // --- Basic ---
      { 
        name: "lookback", 
        label: "Lookback Period", 
        type: "categorical", 
        default: 126, 
        options: [63, 126, 252], 
        category: "basic", 
        optimise: true, 
        integer: true,
        lookback: true,
        info: "Lookback period for momentum calculation \nRequired: int \nSuggested values [63,126,252]"
      },

      // --- Advanced ---
      { 
        name: "volTarget", 
        label: "Volatility Target (%)", 
        type: "categorical", 
        default: 15, 
        options: [5,10,15,20],
        category: "advanced", 
        optimise: true,
        integer: false,
        lookback: false,
        group: "Volatility Rebalancing",
        info: "Volatility target for rebalancing portfolio \nSet Rebalance Frequency to 0 to remove rebalancing \nSuggested bounds [5,20]" 
      },
      { 
        name: "volLookback", 
        label: "Volatility Lookback Period", 
        type: "categorical", 
        default: 20, 
        options: [21, 63, 126, 252], 
        category: "advanced", 
        optimise: true,
        integer: true,
        lookback: true,
        group: "Volatility Rebalancing",
        info: "Lookback period for volatility calculation during rebalancing \nRequired: int \nSet Rebalance Frequency to 0 to remove rebalancing \nSuggested values [21,63,126,252]" 
      },
      { 
        name: "rebalanceFrequency", 
        label: "Rebalance Frequency (days)", 
        type: "categorical", 
        default: 0, 
        options: [0, 1, 5, 10, 20, 60, "onSignal"], 
        category: "advanced", 
        optimise: true, 
        integer: true,
        lookback: false,
        group: "Volatility Rebalancing",
        info: "Frequency with which to rebalance portfolio \nRequired: int or onSignal to rebalance after every trade \nSet to 0 to remove rebalancing \nSuggested values [0, 1, 5, 10, 21, 63, onSignal]" 
      }
    ],
  },

  breakout: {
    label: "Breakout Strategy", 
    type: "breakout",
    params: [
      // --- Basic ---
      { 
        name: "lookback", 
        label: "Lookback Period", 
        type: "number", 
        default: 20, 
        bounds: [5, 100], 
        category: "basic", 
        optimise: true, 
        integer: true,
        lookback: true,
        info: "Lookback period for breakout boundaries \nRequired: int \nSuggested bounds [5,100]" 
      },

      // --- Advanced ---
      { 
        name: "breakoutMultiplier", 
        label: "Breakout Threshold Multiplier", 
        type: "number", 
        default: 0.0, 
        bounds: [0.0, 0.2], 
        category: "advanced", 
        optimise: true, 
        integer: false,
        lookback: false,
        group: "Breakout Threshold Adjustment",
        info: "Multiplier m to add m * range(lookback prices) to breakout threshold \nSuggested bounds [0.0,0.2]" 
      },
    ],
  },

  pairs_trading: {
    label: "Pairs Trading",
    type: "meanReversion",
    params: [
      // --- Basic ---
      { 
        name: "lookback", 
        label: "Lookback Period", 
        type: "number", 
        default: 20, 
        bounds: [20, 200], 
        category: "basic", 
        optimise: true, 
        integer: true,
        lookback: true,
        info: "Lookback period to calculate mean and std of spread between asset prices \nRequired: int \nSuggested bounds [20,200]" 
      },
      { 
        name: "entryZ", 
        label: "Entry Z-Score", 
        type: "number", 
        default: 2, 
        bounds: [1.5, 2.5], 
        category: "basic", 
        optimise: true, 
        integer: false,
        lookback: false,
        info: "z boundary to open position, where z = |(spread - mean_spread) / std_spread| \nRequired: > Exit Z-Score \nSuggested bounds [1.5,2.5]" 
      },
      { 
        name: "exitZ", 
        label: "Exit Z-Score", 
        type: "number", 
        default: 0.5, 
        bounds: [0, 0.5], 
        category: "basic", 
        optimise: true, 
        integer: false,
        lookback: false,
        info: "z boundary to close position, where z = |(spread - mean_spread) / std_spread| \nRequired: < Entry Z-Score \nSuggested bounds [0,0.5]" 
      },

      // --- Advanced ---
      { 
        name: "hedgeRatio", 
        label: "Hedge Ratio (β)", 
        type: "number", 
        default: 1.0, 
        bounds: [0.5, 2.0], 
        category: "advanced", 
        optimise: true, 
        integer: false,
        lookback: false,
        group: "Pairs Trading Adjustments",
        info: "Factor for computing spread where spread = P_A - β * P_B \nSuggested bounds [0.5,2.0]" 
      },
    ],
  },

  custom: {
    label: "Custom",
    params:[],
  },
};
