// compute running drawdown values
export function computeDrawdowns(equityCurve) {
  let peak = equityCurve[0].value;
  return equityCurve.map((point) => {
    peak = Math.max(peak, point.value);
    const drawdown = (peak - point.value) / peak;
    return { date: point.date, drawdown };
  });
}

// map benchmark data to allow for charting
export function mapBenchmark(ohlcv, startDate, initialCapital = 10000) {
  if (!ohlcv || ohlcv.length === 0) return [];
  const sorted = [...ohlcv].sort((a, b) => new Date(a.date) - new Date(b.date));
  const start = new Date(startDate.value);
  const filtered = sorted.filter(d => new Date(d.date) >= start);
  const firstClose = filtered[0].close;
  return filtered.map((d) => ({
    date: d.date, 
    value: (d.close / firstClose) * initialCapital, 
  }));
}

// compute histogram values for trade data
export function getTradeHistogram(trades, mode, bins = 20) {
  if (!trades || trades.length === 0) return [];


  const results = mode === "pnl" ? trades.map((t) => t.pnl) : trades.map((t) => t.returnPct);
  const min = Math.min(...results);
  const max = Math.max(...results);
  const binSize = max === min ? 1 : (max - min) / bins;

  // Group counts per bin per symbol
  const histogram = Array.from({ length: bins }, (_, i) => ({
    bin: (min + binSize * (i + 0.5)).toFixed(2),
  }));

  trades.forEach((t) => {
    const index = mode === "pnl" ? Math.min(Math.floor((t.pnl - min) / binSize), bins - 1) : Math.min(Math.floor((t.returnPct - min) / binSize), bins - 1);
    const sym = t.symbol;
    histogram[index][sym] = (histogram[index][sym] || 0) + 1;
  });

  return histogram;
}
