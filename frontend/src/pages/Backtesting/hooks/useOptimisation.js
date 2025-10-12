import { useState } from "react";

export function useOptimisation() {
  const [optimisationResult, setOptimisationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  

  const optimiseParameters = async ({ symbols, strategyType, basicParams, advancedParams, optimParams, selectedPairs }) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        strategy: strategyType?.value,
        symbols: strategyType?.value === "pairs_trading" ? selectedPairs.map((s) => [s.stock1, s.stock2]) : symbols.map((s) => [s.value]),
        params: {
          ...Object.fromEntries(Object.entries(basicParams).map(([k, v]) => [k, {"value": v.value, "type": v.type, "bounds": v.bounds, "optimise": v.optimise, "integer": v.integer, "category": v.category, "options": v.options}])),
          ...Object.fromEntries(Object.entries(advancedParams).map(([k, v]) => [k, {"value": v.value, "type": v.type, "bounds": v.bounds, "optimise": v.optimise, "integer": v.integer, "category": v.category, "options": v.options}])),
        },
        optimParams: {
          ...Object.fromEntries(Object.entries(optimParams).map(([k, v]) => [k, v.value])),
        }
      };
      const res = await fetch("http://localhost:8000/api/params/optimise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Optimisation failed");
        return;
      }

      const data = await res.json();
      setOptimisationResult(data);
      console.log(data)
      return data;
    } catch (err) {
      setError(err);
      alert("Optimisation failed");
    } finally {
      setIsLoading(false);
    }
  };

  return { optimisationResult, optimiseParameters, isLoading, error };
}
