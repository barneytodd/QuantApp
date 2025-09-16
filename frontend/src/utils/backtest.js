import { computeSMA } from "./indicators";

function computeDailyReturns(equityCurve) {
  let returns = [];
  for (let i = 1; i < equityCurve.length; i++) {
    const prev = equityCurve[i - 1].value;
    const curr = equityCurve[i].value;
    returns.push((curr - prev) / prev);
  }
  return returns;
}

function computeMetrics(equityCurve, riskFreeRate = 0.01) {
  const returns = computeDailyReturns(equityCurve);
  if (returns.length === 0) return null;

  const n = returns.length;
  const meanDaily = returns.reduce((a, b) => a + b, 0) / n;
  const variance = returns.reduce((a, b) => a + Math.pow(b - meanDaily, 2), 0) / n;
  const stdDaily = Math.sqrt(variance);

  const tradingDays = 252; 
  
  // Annualized metrics
  const meanAnnual = meanDaily * tradingDays;
  const volAnnual = stdDaily * Math.sqrt(tradingDays);
  const sharpe = volAnnual > 0 ? (meanAnnual - riskFreeRate) / volAnnual : 0;

  // Max drawdown
  let peak = equityCurve[0].value;
  let maxDrawdown = 0;
  for (let point of equityCurve) {
    peak = Math.max(peak, point.value);
    const drawdown = (peak - point.value) / peak;
    maxDrawdown = Math.max(maxDrawdown, drawdown);
  }

  return {
    mean_return: meanAnnual,
    annualised_volatility: volAnnual,
    sharpe_ratio: sharpe,
    max_drawdown: maxDrawdown * 100, // %
  };
}

function computeTradeStats(trades) {
  if (trades.length === 0) return null;

  const wins = trades.filter(t => t.returnPct > 0);
  const losses = trades.filter(t => t.returnPct <= 0);

  const totalWin = wins.reduce((a, t) => a + t.returnPct*t.entryPrice, 0);
  const totalLoss = losses.reduce((a, t) => a + Math.abs(t.returnPct*t.entryPrice), 0);

  return {
    numTrades: trades.length,
    winRate: (wins.length / trades.length) * 100,
    avgWin: wins.length ? totalWin / wins.length : 0,
    avgLoss: losses.length ? -totalLoss / losses.length : 0,
    profitFactor: totalLoss > 0 ? totalWin / totalLoss : Infinity,
    bestTrade: trades.reduce((a, b) => (a.pnl > b.pnl ? a : b)),
    worstTrade: trades.reduce((a, b) => (a.pnl < b.pnl ? a : b)),
  };
}

export function backtestSMA(data, shortPeriod, longPeriod, initialCapital = 10000) {
  if (!data || data.length === 0) return null;

  const prices = data.map(d => ({
    time: d.date,
    close: d.close,
  }));

  const shortSMA = computeSMA(prices, shortPeriod);
  const longSMA = computeSMA(prices, longPeriod);

  let capital = initialCapital;
  let position = 0; 
  let equityCurve = [];
  let trades = [];
  let entryPrice = null;
  let entryDate = null;

  for (let i = 0; i < prices.length; i++) {
    const p = prices[i];
    const short = shortSMA[i]?.value;
    const long = longSMA[i]?.value;

    if (!short || !long) {
      equityCurve.push({ date: p.time, value: capital + position * p.close });
      continue;
    }

    // Buy signal
    if (short > long && position === 0) {
      position = capital / p.close; 
      capital = 0;
      entryPrice = p.close;
      entryDate = p.time;
    }

    // Sell signal
    if (short < long && position > 0) {
      const exitPrice = p.close;
      const pnl = position * exitPrice - initialCapital; // relative to initial capital
      const returnPct = ((exitPrice - entryPrice) / entryPrice) * 100;
      trades.push({
        entryDate,
        exitDate: p.time,
        entryPrice,
        exitPrice,
        pnl,
        returnPct,
        holdingPeriod: trades.length, // placeholder until we compute properly
      });

      capital = position * exitPrice;
      position = 0;
      entryPrice = null;
      entryDate = null;
    }

    const totalValue = capital + position * p.close;
    equityCurve.push({ date: p.time, value: totalValue });
  }

  // Final liquidation
  if (position > 0) {
    const lastPrice = prices[prices.length - 1].close;
    const pnl = position * lastPrice - initialCapital;
    const returnPct = ((lastPrice - entryPrice) / entryPrice) * 100;
    trades.push({
      entryDate,
      exitDate: prices[prices.length - 1].time,
      entryPrice,
      exitPrice: lastPrice,
      pnl,
      returnPct,
    });

    capital = position * lastPrice;
    position = 0;
  }
      
  const metrics = computeMetrics(equityCurve);
  const tradeStats = computeTradeStats(trades);

  return {
    initialCapital,
    finalCapital: capital,
    returnPct: (capital / initialCapital - 1) * 100,
    equityCurve,
    metrics,
    trades,
    tradeStats,
  };
}
