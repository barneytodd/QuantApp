import { useState, useCallback } from "react";

export function usePairs() {
  const [pairCandidates, setPairCandidates] = useState([]);
  const [selectedPairs, setSelectedPairs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const selectPairs = useCallback (async (symbols, weights = { w_corr: 0.5, w_coint: 0.5 }) => {
    if (!symbols || symbols.length < 2) {
      throw new Error("Select at least two symbols to generate pairs.");
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("http://localhost:8000/api/pairs/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbols,
          ...weights,
        }),
      });

      if (!res.ok) throw new Error("Failed to fetch pair analysis");

      const data = await res.json();
      setPairCandidates(data.all_pairs);
      setSelectedPairs(data.selected_pairs);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { pairCandidates, selectedPairs, setSelectedPairs, selectPairs, isLoading, error };
}

