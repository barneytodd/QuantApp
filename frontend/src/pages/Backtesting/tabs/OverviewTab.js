import { useState, useMemo } from "react";
import EquityChart from "../charts/EquityChart";
import { mapBenchmark } from "../charts/chartCalcs";
import MetricCard from "../../../components/ui/MetricCard";

export function OverviewTab({ results, benchmark, startDate, showIndividual=true, extraStats=true }) {
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
        {extraStats && (
          <MetricCard label="Initial Capital" value={10000} type="currency" />
        )}
        <MetricCard label="Final Capital"  value={selectedResult.finalCapital ?? "-"} type="currency" />
        <MetricCard label="Return %" value={selectedResult.returnPct ?? "-"} type="percentage" />
        {extraStats && (
          <MetricCard 
            label="Metric Score" 
            value={
              0.5 * (selectedResult.metrics.sharpe_ratio ?? 0) / 2
              + 0.3 * (selectedResult.metrics.cagr ?? 0) / 20
              + 0.2 * (1 - (selectedResult.metrics.max_drawdown ?? 100)/40)
            }/>
        )}
        <MetricCard label="Sharpe Ratio" value={selectedResult.metrics.sharpe_ratio ?? "-"} />
        {extraStats && (
          <MetricCard label="CAGR" value={selectedResult.metrics.cagr ?? "-"} />
        )}
        <MetricCard label="Max Drawdown" value={selectedResult.metrics.max_drawdown ?? "-"} type="percentage"/>
        {extraStats && (
          <MetricCard label="Volatility" value={selectedResult.metrics.annualised_volatility * 100 ?? "-"} type="percentage"/>
        )}
      </div>

      {/* Equity Curve */}
      <div className="bg-white p-4 shadow rounded">
        <h3 className="font-bold mb-2">Equity Curve</h3>
        <EquityChart
          equityData={equityData}
          benchmarkData={mapBenchmark(benchmark, startDate, selectedResult.initialCapital)}
          highlightOverall={selectedTicker === "overall"}
        />
      </div>

    </div>
  );
}

export default OverviewTab;
