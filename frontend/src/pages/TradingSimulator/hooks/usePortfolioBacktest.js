import { useState } from "react";

/**
 * Custom React hook to run backtests for trading strategies.
 *
 * @returns {Object} Contains:
 *  - backtestResult {Object|null}: The result returned from the backtest API.
 *  - runBacktest {Function}: Async function to execute the backtest.
 *  - isLoading {boolean}: True if backtest is currently running.
 *  - error {Error|null}: Any error encountered during backtest execution.
 */
export function usePortfolioBacktest() {
  const [backtestResult, setBacktestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const runBacktest = async (portfolios) => {
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("http://localhost:8000/api/strategies/backtest/portfolios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(portfolios),
      });

      if (!res.ok) {
        alert("Backtest failed");
        return; 
      }
      const data = await res.json();
      setBacktestResult(data);
      return data;
    } catch (err) {
      setError(err);
      alert("Backtest failed");
    } finally {
      setIsLoading(false);
    }
  };

  return { backtestResult, runBacktest, isLoading, error };
}
