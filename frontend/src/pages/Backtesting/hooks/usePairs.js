import { useState, useCallback } from "react";

export function usePairs() {
  const [pairCandidates, setPairCandidates] = useState([]);
  const [selectedPairs, setSelectedPairs] = useState([]);
  const [progress, setProgress] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  
  const selectPairs = useCallback(async (symbols, weights = { w_corr: 0.5, w_coint: 0.5 }) => {
    if (!symbols || symbols.length < 2) {
      setSelectedPairs([]);
      alert("Select at least two symbols to generate pairs.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setProgress({});

    try {
      // 1️⃣ Start background task
      const startRes = await fetch("http://localhost:8000/api/pairs/select/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbols, ...weights }),
      });

      if (!startRes.ok) throw new Error("Failed to start pair selection task");
      const { task_id } = await startRes.json();
      if (!task_id) throw new Error("No task_id returned from backend");


      // 2️⃣ Stream SSE progress
      await new Promise((resolve, reject) => {
        const evtSource = new EventSource(`http://localhost:8000/api/pairs/select/stream/${task_id}`);

        evtSource.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);

            if (data.error) {
              setError(data.error);
              evtSource.close();
              setIsLoading(false);
              reject(data.error);
              return;
            }

            // Update progress
            if (data.done && data.total) {
              setProgress({"completed": data.done, "total": data.total});
            }

            // Task completed
            if (data.status === "done") {
              evtSource.close();
              resolve();
            }
          } catch (err) {
            console.error("SSE parse error:", err);
          }
        };

        evtSource.onerror = (err) => {
          console.error("SSE error:", err);
          evtSource.close();
          setError("SSE connection lost");
          setIsLoading(false);
          reject(err);
        };
      });

      // 3️⃣ Fetch final results
      const resultsRes = await fetch(`http://localhost:8000/api/pairs/select/results/${task_id}`);
      if (!resultsRes.ok) throw new Error("Failed to fetch pair results");
      const data = await resultsRes.json();

      setPairCandidates(data.all_pairs || []);
      setSelectedPairs(data.selected_pairs || []);

      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      console.error("Pair selection failed:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    pairCandidates,
    selectedPairs,
    setSelectedPairs,
    selectPairs,
    progress,
    isLoading,
    error,
  };
}
