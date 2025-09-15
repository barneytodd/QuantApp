import { computeSMA } from "./indicators"

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
  const sharpe = (meanAnnual - riskFreeRate) / volAnnual;

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
    max_drawdown: maxDrawdown,
  };
}

export function backtestSMA(data, shortPeriod, longPeriod, initialCapital = 10000) {
    if (!data || data.length === 0) return null;
    // Ensure data has time + close
    const prices = data.map(d => ({
        time: d.date,
        close: d.close,
    }));

    // Compute moving averages
    const shortSMA = computeSMA(prices, shortPeriod);
    const longSMA = computeSMA(prices, longPeriod);

    let capital = initialCapital;
    let position = 0; 
    let equityCurve = [];

    for (let i = 0; i < prices.length; i++) {
        const p = prices[i];
        const short = shortSMA[i]?.value;
        const long = longSMA[i]?.value;
        if (!short || !long) {
        equityCurve.push({ date: p.time, value: capital });
        continue;
        }

        // Buy signal
        if (short > long && position === 0) {
        position = capital / p.close; // buy shares
        capital = 0;
        }

        // Sell signal
        if (short < long && position > 0) {
        capital = position * p.close; // sell all
        position = 0;
        }

        // Update equity
        const totalValue = capital + position * p.close;
        equityCurve.push({ date: p.time, value: totalValue });
    }

    // Final liquidation
    if (position > 0) {
        capital = position * prices[prices.length - 1].close;
        position = 0;
    }
        
    const metrics = computeMetrics(equityCurve);
    
    return {
    finalCapital: capital,
    equityCurve,
    returnPct: (capital / initialCapital - 1) * 100,
    metrics,
    };
}