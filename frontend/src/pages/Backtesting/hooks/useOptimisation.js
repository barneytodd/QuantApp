import { useState } from "react";

export function useOptimisation() {

  const [optimisationResult, setOptimisationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const optimiseParameters = async ({ symbols, strategyType, basicParams, advancedParams }) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        symbols: symbols.map((s) => s.value),
        strategy: strategyType.value,
        params: {
          ...Object.fromEntries(Object.entries(basicParams).map(([k, v]) => [k, v.value])),
          ...Object.fromEntries(Object.entries(advancedParams).map(([k, v]) => [k, v.value])),
        },
      };
      console.log(payload)
      const res = await fetch("http://localhost:8000/api/params/optimise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Optimisation failed");

      const data = await res.json();
      setOptimisationResult(data);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { optimisationResult, optimiseParameters, isLoading, error };
}
