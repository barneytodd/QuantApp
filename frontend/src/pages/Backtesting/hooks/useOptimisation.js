import { useState } from "react";

export function useOptimisation() {
  const [optimisationResult, setOptimisationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  

  const optimiseParameters = async ({ symbols, strategyType, basicParams, advancedParams, optimParams }) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        symbols: symbols.map((s) => s.value),
        strategy: strategyType.value,
        params: {
          ...Object.fromEntries(Object.entries(basicParams).map(([k, v]) => [k, {"value": v.value, "type": v.type, "bounds": v.bounds, "optimise": v.optimise, "integer": v.integer, "category": v.category}])),
          ...Object.fromEntries(Object.entries(advancedParams).map(([k, v]) => [k, {"value": v.value, "type": v.type, "bounds": v.bounds, "optimise": v.optimise, "integer": v.integer, "category": v.category}])),
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
