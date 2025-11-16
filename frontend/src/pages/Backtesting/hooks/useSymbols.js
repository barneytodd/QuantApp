import { useState, useEffect } from "react";
import { getApiUrl } from "../../../utils/apiUrl";


export function useSymbols() {
  const [symbols, setSymbols] = useState([]);
  const [benchmarkData, setBenchmarkData] = useState(null);

  useEffect(() => {
    fetch(`${getApiUrl()}/api/symbols/db_symbols`)
      .then((res) => res.json())
      .then((data) => {
        setSymbols(
          data
            .filter((s) => s !== "SPY")
            .map((s) => ({ value: s, label: s }))
        );
      });

    fetch(`${getApiUrl()}/api/data/ohlcv/SPY?limit=500`)
      .then((res) => res.json())
      .then((data) => setBenchmarkData(data));
  }, []);

  return { symbols, benchmarkData };
}
