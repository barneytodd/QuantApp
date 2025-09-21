import DrawdownChart from "../charts/DrawdownChart";
import { useState } from "react";
import MetricCard from "../../../components/ui/MetricCard";


export function RiskExposureTab({ results }) {
  const [selectedTicker, setSelectedTicker] = useState("overall");
  
  // List of tickers excluding "overall"
  const tickers = results
    .filter(r => r.symbol && r.symbol !== "overall")
    .map(r => r.symbol);

  // Selected ticker object
  const selectedResult = results.find(r => r.symbol === selectedTicker);

  const { metrics } = selectedResult;

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

      {/* Risk metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <MetricCard label="Annualised Return" value={metrics?.mean_return != null ? metrics.mean_return * 100 : "-"} type="percentage" />
        <MetricCard label="Volatility" value={metrics?.annualised_volatility != null ? metrics.annualised_volatility * 100 : "-"} type="percentage" />
        <MetricCard label="Sharpe Ratio" value={metrics.sharpe_ratio ?? "-"} />
      </div>

      {/* Equity Curve */}
      <div className="bg-white p-4 shadow rounded">
        <h3 className="font-bold mb-2">Drawdown Chart</h3>
        <DrawdownChart equityCurve={selectedResult.equityCurve}/>
      </div>
    </div>
  );
}

export default RiskExposureTab;
