export function computeDrawdowns(equityCurve) {
  let peak = equityCurve[0].value;
  return equityCurve.map((point) => {
    peak = Math.max(peak, point.value);
    const drawdown = (peak - point.value) / peak;
    return { date: point.date, drawdown };
  });
}

export function mapBenchmark(ohlcv, initialCapital = 10000) {
  if (!ohlcv || ohlcv.length === 0) return [];

  const firstClose = ohlcv[0].close;

  return ohlcv.map((d) => ({
    date: d.date, // keep same date as backtest
    value: (d.close / firstClose) * initialCapital, // normalize to initial capital
  }));
}

export function getPnlHistogram(trades, bins = 20) {
  if (!trades || trades.length === 0) return [];

  const pnls = trades.map((t) => t.pnl);

  const min = Math.min(...pnls);
  const max = Math.max(...pnls);
  
  // Prevent division by zero if all trades have same P&L
  const binSize = max === min ? 1 : (max - min) / bins;

  const histogram = Array(bins).fill(0);

  pnls.forEach((p) => {
    const index = Math.min(Math.floor((p - min) / binSize), bins - 1);
    histogram[index]++;
  });

  // Compute bin center values for the x-axis
  return histogram.map((count, i) => ({
    bin: (min + binSize * (i + 0.5)).toFixed(2),
    count,
  }));
}
