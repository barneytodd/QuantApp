// compute returns for strategy backtest
function computeDailyReturns(equityCurve) {
  let returns = [];
  for (let i = 1; i < equityCurve.length; i++) {
    const prev = equityCurve[i - 1].value;
    const curr = equityCurve[i].value;
    returns.push((curr - prev) / prev);
  }
  return returns;
}

// compute metrics for strategy backtest
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
    max_drawdown: maxDrawdown * 100,
  };
}

// compute trade stats for strategy backtest
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

// calculate commission for each trade 
function commission(signal = "buy", capital = 0, effective_price = 0, position = 0, commission_pct = 0.001, commission_fixed = 0.0) {
  let com = 0;
  if (signal === "buy") {
    // maximises the size of trade
    com = (capital * commission_pct + commission_fixed * effective_price) / (effective_price + commission_pct) 
  }
  else {
    com = position * commission_pct + commission_fixed
  }
  return com
}

// run backtest for selected strategy
export function runBacktest(data, params, signalGenerator, initialCapital = 10000, slippage_pct = 0.0005) {
  let symbol = data[0].symbol;
  let capital = initialCapital;
  let position = 0;
  let equityCurve = [];
  let trades = [];
  let entryPrice = null;
  let entryDate = null;

  for (let i = 0; i < data.length; i++) {
    const price = data[i].close;
    const signal = signalGenerator(data, i, params);

    if (signal === "buy" && position === 0) {
      const effective_price = price * (1 + slippage_pct);
      position = (capital - commission(signal, capital, effective_price, 0)) / effective_price;
      capital = 0;
      entryPrice = price;
      entryDate = data[i].date;
    }

    if (signal === "sell" && position > 0) {
      const exitPrice = price;
      const effectiveExitPrice = exitPrice * (1 - slippage_pct);
      const effectiveEntryPrice = entryPrice * (1 + slippage_pct)
      const pnl = position * (effectiveExitPrice - effectiveEntryPrice);
      const returnPct = ((effectiveExitPrice - effectiveEntryPrice) / effectiveEntryPrice) * 100;
      trades.push({
        symbol,
        entryDate,
        exitDate: data[i].date,
        entryPrice,
        exitPrice,
        pnl,
        returnPct,
      });
      capital = position * effectiveExitPrice - commission(signal, 0, 0, position);
      position = 0;
      entryPrice = null;
      entryDate = null;
    }

    equityCurve.push({ date: data[i].date, value: capital + position * price });
  }

  // Final liquidation
  if (position > 0) {
    const lastPrice = data[data.length - 1].close;
    const effectiveLastPrice = lastPrice * (1 - slippage_pct)
    const effectiveEntryPrice = entryPrice * (1 + slippage_pct)
    const pnl = position * (effectiveLastPrice - effectiveEntryPrice);
    const returnPct = ((effectiveLastPrice - effectiveEntryPrice) / effectiveEntryPrice) * 100;
    trades.push({
      symbol,
      entryDate,
      exitDate: data[data.length - 1].date,
      entryPrice,
      exitPrice: lastPrice,
      pnl,
      returnPct,
    });
    capital = position * lastPrice - commission("sell", 0, 0, position);
  }

  return {
    symbol,
    initialCapital,
    finalCapital: capital,
    returnPct: (capital / initialCapital - 1) * 100,
    equityCurve,
    trades,
    metrics: computeMetrics(equityCurve),
    tradeStats: computeTradeStats(trades),
  };
}

// combine multi-stock backtest results to get overall portfolio results
export function combineResults(results) {
  const dateMap = new Map();

  // Collect all unique dates
  results.forEach(r => {
    r.equityCurve.forEach(point => {
      if (!dateMap.has(point.date)) dateMap.set(point.date, []);
    });
  });

  // Sum values per date, carrying forward the last known value for each ticker
  const combinedCurve = Array.from(dateMap.keys())
    .sort() 
    .map(date => {
      let totalValue = 0;

      results.forEach(r => {
        // Find the last value on or before this date
        const lastPoint = [...r.equityCurve]
          .filter(p => p.date <= date)
          .sort((a, b) => a.date.localeCompare(b.date))
          .pop();

        totalValue += lastPoint ? lastPoint.value : r.initialCapital;
      });

      return { date, value: totalValue };
    });

  const combinedTrades = results.flatMap(r => r.trades);

  const initialCapital = results.reduce((sum, r) => sum + r.initialCapital, 0);
  const finalCapital = combinedCurve[combinedCurve.length - 1].value;

  return {
    symbol: "overall",
    initialCapital,
    finalCapital,
    returnPct: (finalCapital / initialCapital - 1) * 100,
    equityCurve: combinedCurve,
    trades: combinedTrades,
    metrics: computeMetrics(combinedCurve),
    tradeStats: computeTradeStats(combinedTrades),
  };
}