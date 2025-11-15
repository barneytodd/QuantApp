import { useState, useEffect } from "react";

const server = process.env.REACT_APP_ENV === "local" ? "localhost" : "backend";
const API_URL = `http://${server}:${process.env.REACT_APP_BACKEND_PORT}`;

export function useSymbols() {
  const [symbols, setSymbols] = useState([]);
  const [benchmarkData, setBenchmarkData] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/symbols/db_symbols`)
      .then((res) => res.json())
      .then((data) => {
        setSymbols(
          data
            .filter((s) => s !== "SPY")
            .map((s) => ({ value: s, label: s }))
        );
      });

    fetch(`${API_URL}/api/data/ohlcv/SPY?limit=500`)
      .then((res) => res.json())
      .then((data) => setBenchmarkData(data));
  }, []);

  return { symbols, benchmarkData };
}
