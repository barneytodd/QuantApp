import { computeSMA, computeBollingerBands, computeRSI } from "../../../utils/indicators";

export function smaSignalGenerator(data, i, params) {
  const { shortPeriod, longPeriod } = params;
  if (i < longPeriod) return "hold";

  const short = computeSMA(data, shortPeriod)[i]?.value;
  const long = computeSMA(data, longPeriod)[i]?.value;

  if (!short || !long) return "hold";
  if (short > long) return "buy";
  if (short < long) return "sell";
  return "hold";
}


export function bollingerSignalGenerator(data, i, params) {
  const { period, stdDev } = params;
  const bands = computeBollingerBands(data, period, stdDev);
  const price = data[i].close;

  if (!bands[i]) return "hold";
  if (price < bands[i].lower) return "buy";
  if (price > bands[i].upper) return "sell";
  return "hold";
}

export function rsiSignalGenerator(data, i, params) {
  const { period, oversold, overbought } = params;
  const rsiSeries = computeRSI(data, period);

  const rsi = rsiSeries[i]?.value;
  if (!rsi) return "hold";

  if (rsi < oversold) return "buy";
  if (rsi > overbought) return "sell";
  return "hold";
}


export function momentumSignalGenerator(data, i, params) {
  const { lookback } = params;
  if (i < lookback) return "hold";

  const pastPrice = data[i - lookback].close;
  const currentPrice = data[i].close;

  if (currentPrice > pastPrice) return "buy";  // positive momentum
  if (currentPrice < pastPrice) return "sell"; // negative momentum
  return "hold";
}

export function breakoutSignalGenerator(data, i, params) {
  const { lookback } = params;
  if (i < lookback) return "hold";

  const window = data.slice(i - lookback, i);
  const highs = window.map(d => d.close);
  const lows = window.map(d => d.close);

  const maxHigh = Math.max(...highs);
  const minLow = Math.min(...lows);
  const price = data[i].close;

  if (price > maxHigh) return "buy";
  if (price < minLow) return "sell";
  return "hold";
}

export function pairsSignalGenerator(data, i, params) {
  const { symbol1, symbol2, lookback, entryZ, exitZ } = params;

  if (i < lookback) return "hold";

  // Calculate spread: simple price difference or log ratio
  const price1 = data[i][symbol1];
  const price2 = data[i][symbol2];
  const spreadSeries = data.slice(i - lookback, i).map(d => d[symbol1] - d[symbol2]);
  const mean = spreadSeries.reduce((a, b) => a + b, 0) / spreadSeries.length;
  const std = Math.sqrt(spreadSeries.reduce((a, b) => a + (b - mean) ** 2, 0) / spreadSeries.length);

  const spread = price1 - price2;
  const zScore = (spread - mean) / std;

  if (zScore > entryZ) return "short";  // short spread: sell symbol1, buy symbol2
  if (zScore < -entryZ) return "long";  // long spread: buy symbol1, sell symbol2
  if (Math.abs(zScore) < exitZ) return "exit";

  return "hold";
}


