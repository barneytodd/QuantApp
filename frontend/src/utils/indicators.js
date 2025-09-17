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

export function computeRSI(data, period = 14) {
  if (data.length < period) return [];

  let gains = [];
  let losses = [];
  let rsi = [];

  for (let i = 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? -change : 0);

    if (i >= period) {
      const avgGain = gains.slice(-period).reduce((a, b) => a + b, 0) / period;
      const avgLoss = losses.slice(-period).reduce((a, b) => a + b, 0) / period;
      const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
      const value = 100 - 100 / (1 + rs);

      rsi.push({ date: data[i].date, value });
    } else {
      rsi.push({ date: data[i].date, value: null });
    }
  }

  return rsi;
}
