// compute values for SMA series
export function computeSMA(data, period) {
  const sma = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      sma.push({ time: data[i].time, value: null });
    } else {
      const slice = data.slice(i - period + 1, i + 1);
      const sum = slice.reduce((acc, d) => acc + d.close, 0);
      sma.push({ time: data[i].time, value: sum / period });
    }
  }
  return sma;
}

// compute values for EMA series
export function computeEMA(prices, period) {
  if (!prices || prices.length < period) return [];

  const k = 2 / (period + 1); // smoothing factor
  const emaArray = [];

  // Seed EMA with first SMA
  let sum = 0;
  for (let i = 0; i < period; i++) sum += prices[i].close;
  let emaPrev = sum / period;
  emaArray[period - 1] = { time: prices[period - 1].time, value: emaPrev };

  // Compute EMA for the rest
  for (let i = period; i < prices.length; i++) {
    const price = prices[i].close;
    emaPrev = price * k + emaPrev * (1 - k);
    emaArray[i] = { time: prices[i].time, value: emaPrev };
  }

  // Fill initial values with null for alignment
  for (let i = 0; i < period - 1; i++) {
    emaArray[i] = { time: prices[i].time, value: null };
  }

  return emaArray;
}

// compute values for bollinger bands
export function computeBollingerBands(prices, period = 20, stdDevMultiplier = 2) {
  if (!prices || prices.length < period) return [];

  const bands = [];

  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      bands.push({ time: prices[i].time, upper: null, middle: null, lower: null });
      continue;
    }

    // Extract the window of values for this period
    const window = prices.slice(i - period + 1, i + 1).map(p => p.close);

    // Compute mean (middle band)
    const mean = window.reduce((a, b) => a + b, 0) / period;

    // Compute standard deviation
    const variance = window.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / period;
    const stdDev = Math.sqrt(variance);

    // Upper and lower bands
    const upper = mean + stdDevMultiplier * stdDev;
    const lower = mean - stdDevMultiplier * stdDev;

    bands.push({ time: prices[i].time, upper, middle: mean, lower });
  }

  return bands;
}

// detect where short and long SMA series cross for buy/sell markers
export function detectCrossovers(shortSMA, longSMA, ohlcv, shortPeriod, longPeriod) {
  const signals = [];
  const startIndex = Math.max(shortPeriod, longPeriod);

  for (let i = startIndex; i < shortSMA.length; i++) {
    // Skip if SMA values are missing
    if (!shortSMA[i]?.value || !longSMA[i]?.value) continue;
    if (!shortSMA[i - 1]?.value || !longSMA[i - 1]?.value) continue;
    if (!ohlcv[i]) continue;

    // Buy signal
    if (shortSMA[i - 1].value <= longSMA[i - 1].value &&
        shortSMA[i].value > longSMA[i].value) {
      signals.push({
        time: shortSMA[i].time,
        type: "buy",
        value: ohlcv[i].close,
        smaValue: shortSMA[i].value
      });
    }

    // Sell signal
    if (shortSMA[i - 1].value >= longSMA[i - 1].value &&
        shortSMA[i].value < longSMA[i].value) {
      signals.push({
        time: shortSMA[i].time,
        type: "sell",
        value: ohlcv[i].close,
        smavalue: shortSMA[i].value
      });
    }
  }
  return signals;
}
