import { useState } from "react";

const server = process.env.REACT_APP_ENV === "local" ? "localhost" : "backend";
const API_URL = `http://${server}:${process.env.REACT_APP_BACKEND_PORT}`;

/**
 * Custom React hook to run backtests for trading strategies.
 *
 * @returns {Object} Contains:
 *  - backtestResult {Object|null}: The result returned from the backtest API.
 *  - runBacktest {Function}: Async function to execute the backtest.
 *  - isLoading {boolean}: True if backtest is currently running.
 *  - error {Error|null}: Any error encountered during backtest execution.
 */
export function useBacktest() {
  const [backtestResult, setBacktestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Runs a backtest with the given parameters.
   *
   * @async
   * @param {Object} params - Parameters for the backtest
   * @param {Array} params.symbolItems - Array of selected symbol objects containing symbol(s), strategy and weight info
   * @param {Object} params.basicParams - Basic parameters for the strategy
   * @param {Object} params.advancedParams - Advanced parameters for the strategy
   * @returns {Promise<Object|undefined>} Resolves with API response data if successful
   */
  const runBacktest = async ({ symbolItems, basicParams, advancedParams }) => {
    setIsLoading(true);
    setError(null);

    try {
      const symbolItemsWithWeights = symbolItems
        .map(item => {
          const weightParam = item.strategy === "pairs_trading" 
            ? advancedParams[`${item.symbols[0]}-${item.symbols[1]}_weight`] 
            : advancedParams[`${item.symbols[0]}_weight`];
          return {
            ...item,
            weight: item.weight ?? weightParam?.value ?? 0
          };
        })
        .filter(item => item.weight !== 0);
    
      const payload = {
        symbolItems: symbolItemsWithWeights,
        params: Object.fromEntries(
          Object.entries(advancedParams)
            .filter(([key, _]) => !key.endsWith("_weight"))
            .map(([k, v]) => [k, { value: v.value, lookback: v.lookback ?? false }])
            .concat(
              Object.entries(basicParams).map(([k, v]) => [k, { value: v.value, lookback: v.lookback ?? false }])
            )
        ),
      };

      const res = await fetch(`${API_URL}/api/strategies/backtest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
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
