import { useState, useMemo } from "react";
import EquityChart from "../charts/EquityChart";
import { mapBenchmark } from "../charts/chartCalcs";

export function OverviewTab({ results, benchmark }) {
  const [selectedTicker, setSelectedTicker] = useState("overall");

  // List of tickers excluding "overall"
  const tickers = results
    .filter(r => r.symbol && r.symbol !== "overall")
    .map(r => r.symbol);

  // Selected ticker object
  const selectedResult = results.find(r => r.symbol === selectedTicker);

  // Prepare equity data for the chart
  const equityData = useMemo(() => {
    if (selectedTicker !== "overall") return [selectedResult];

    return results;
  }, [results, selectedTicker, selectedResult]);

  return (
    <div className="space-y-4">
      {/* Ticker-view Dropdown */}
      <div className="flex justify-end">
        <select
          className="border rounded p-2 text-sm"
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
        >
          <option value="overall">Overall portfolio results</option>
          {tickers.map((ticker) => (
            <option key={ticker} value={ticker}>
              {ticker}
            </option>
          ))}
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 shadow rounded">
          <p className="text-sm text-gray-500">Final Capital</p>
          <p className="text-lg font-bold">
            ${selectedResult.finalCapital.toFixed(2)}
          </p>
        </div>
        <div className="bg-white p-4 shadow rounded">
          <p className="text-sm text-gray-500">Return %</p>
          <p className="text-lg font-bold">
            {selectedResult.returnPct.toFixed(2)}%
          </p>
        </div>
        <div className="bg-white p-4 shadow rounded">
          <p className="text-sm text-gray-500">Sharpe Ratio</p>
          <p className="text-lg font-bold">
            {selectedResult.metrics.sharpe_ratio?.toFixed(2) ?? "-"}
          </p>
        </div>
        <div className="bg-white p-4 shadow rounded">
          <p className="text-sm text-gray-500">Max Drawdown</p>
          <p className="text-lg font-bold">
            {selectedResult.metrics.max_drawdown?.toFixed(2) ?? "-"}%
          </p>
        </div>
      </div>

      {/* Equity Curve */}
      <div className="bg-white p-4 shadow rounded">
        <h3 className="font-bold mb-2">Equity Curve</h3>
        <EquityChart
          equityData={equityData}
          benchmarkData={mapBenchmark(benchmark, selectedResult.initialCapital)}
          highlightOverall={selectedTicker === "overall"}
        />
      </div>

    </div>
  );
}

export default OverviewTab;
