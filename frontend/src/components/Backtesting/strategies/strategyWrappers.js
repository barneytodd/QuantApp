import { runBacktest } from "../backtestEngine";
import { smaSignalGenerator, bollingerSignalGenerator, rsiSignalGenerator, momentumSignalGenerator, breakoutSignalGenerator, pairsSignalGenerator } from "./buySellSignalGenerators";

// wrappers for backtest function for each strategy type

export function backtestSMA(data, params, initialCapital) {
  return runBacktest(data, params, smaSignalGenerator, initialCapital);
}

export function backtestBollinger(data, params, initialCapital) {
  return runBacktest(data, params, bollingerSignalGenerator, initialCapital);
}

export function backtestRSI(data, params, initialCapital = 10000) {
  return runBacktest(data, params, rsiSignalGenerator, initialCapital);
}

export function backtestMomentum(data, params, initialCapital = 10000) {
  return runBacktest(data, params, momentumSignalGenerator, initialCapital);
}

export function backtestBreakout(data, params, initialCapital = 10000) {
  return runBacktest(data, params, breakoutSignalGenerator, initialCapital);
}

export function backtestPairs(data, params, initialCapital = 10000) {
  return runBacktest(data, params, pairsSignalGenerator, initialCapital);
}