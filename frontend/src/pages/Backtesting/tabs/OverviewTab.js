import { useState, useMemo } from "react";
import EquityChart from "../charts/EquityChart";
import { mapBenchmark } from "../charts/chartCalcs";
import MetricCard from "../../../components/ui/MetricCard";

export function OverviewTab({ results, benchmark, showIndividual=true }) {
  const [selectedTicker, setSelectedTicker] = useState("overall");
  // List of tickers excluding "overall"
  const tickers = results
    .filter(r => r.symbol && r.symbol !== "overall")
    .map(r => r.symbol);

  // Selected ticker object
  const selectedResult = results.find(r => r.symbol === selectedTicker);
  // Prepare equity data for the chart
  const equityData = useMemo(() => {
    if (selectedTicker !== "overall" || !showIndividual) return [selectedResult];
    return results;
  }, [results, selectedTicker, selectedResult, showIndividual]);

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
        <MetricCard label="Final Capital"  value={selectedResult.finalCapital ?? "-"} type="currency" />
        <MetricCard label="Return %" value={selectedResult.returnPct ?? "-"} type="percentage" />
        <MetricCard label="Sharpe Ratio" value={selectedResult.metrics.sharpe_ratio ?? "-"} />
        <MetricCard label="Max Drawdown" value={selectedResult.metrics.max_drawdown ?? "-"} type="percentage"/>
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
