import { useState } from "react";

export function useBacktest() {
  const [backtestResult, setBacktestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const runBacktest = async ({ symbols, strategyType, basicParams, advancedParams, selectedPairs }) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        strategy: strategyType.value,
        symbols: symbols.map((s) => s.value),
        params: {
          ...Object.fromEntries(Object.entries(basicParams).map(([k, v]) => [k, v.value])),
          ...Object.fromEntries(Object.entries(advancedParams).map(([k, v]) => [k, v.value])),
        },
        pairs: strategyType.value === "pairs_trading" ? selectedPairs : undefined,
      };

      const res = await fetch("http://localhost:8000/api/strategies/backtest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Backtest failed");

      const data = await res.json();
      setBacktestResult(data);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { backtestResult, runBacktest, isLoading, error };
}
