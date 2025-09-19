import TradeHistogram from "../charts/TradeHistogram";
import { useState } from "react"

export function TradeAnalyticsTab({ results }) {
  const [selectedTicker, setSelectedTicker] = useState("overall");
  const [histogramMode, setHistogramMode] = useState("PnL");

  // List of tickers excluding "overall"
  const tickers = results
    .filter(r => r.symbol && r.symbol !== "overall")
    .map(r => r.symbol);

  // Selected ticker object
  const selectedResult = results.find(r => r.symbol === selectedTicker);

  return (
    <div className="space-y-4">
      {/* Ticker-view Dropdown */}
      <div className="flex justify-end">
        <select
          className="border rounded p-2 text-sm"
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
        >
          <option value="overall">All portfolio trades</option>
          {tickers.map((ticker) => (
            <option key={ticker} value={ticker}>
              {ticker}
            </option>
          ))}
        </select>
      </div>

      {/* Trade stats summary */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Trades</p>
          <p className="text-lg font-bold">{selectedResult.tradeStats.numTrades}</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Win Rate</p>
          <p className="text-lg font-bold">{selectedResult.tradeStats.winRate.toFixed(1)}%</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Profit Factor</p>
          <p className="text-lg font-bold">{selectedResult.tradeStats.profitFactor.toFixed(2)}</p>
        </div>
      </div>
      
      {/* Trade table */}
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="font-bold mb-2">Trade History</h3>
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b">
              <th classNAme="text-left p-2">Ticker</th>
              <th className="text-left p-2">Entry</th>
              <th className="text-left p-2">Exit</th>
              <th className="text-left p-2">Entry Px</th>
              <th className="text-left p-2">Exit Px</th>
              <th className="text-left p-2">PnL ($)</th>
              <th className="text-left p-2">Return %</th>
            </tr>
          </thead>
          <tbody>
            {selectedResult.trades
              .slice()
              .sort((a, b) => new Date(a.exitDate) - new Date(b.exitDate))
              .map((t, i) => (
              <tr key={i} className="border-b">
                <td className="p-2">{t.symbol}</td>
                <td className="p-2">{t.entryDate}</td>
                <td className="p-2">{t.exitDate}</td>
                <td className="p-2">{t.entryPrice.toFixed(2)}</td>
                <td className="p-2">{t.exitPrice.toFixed(2)}</td>
                <td
                  className={`p-2 ${t.pnl >= 0 ? "text-green-600" : "text-red-600"}`}
                >
                  {t.pnl.toFixed(2)}
                </td>
                <td
                  className={`p-2 ${t.returnPct >= 0 ? "text-green-600" : "text-red-600"}`}
                >
                  {t.returnPct.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Trade Distribution */}
      
      <div className="bg-white p-4 shadow rounded">
        <h3 className="font-bold mb-2">Trade Distribution</h3>
        <div className="flex gap-4 items-center">
          <label>
            <input
              type="radio"
              value="PnL"
              checked={histogramMode === "PnL"}
              onChange={() => setHistogramMode("PnL")}
            />
            PnL ($)
          </label>
          <label>
            <input
              type="radio"
              value="Return %"
              checked={histogramMode === "Return %"}
              onChange={() => setHistogramMode("Return %")}
            />
            Return (%)
          </label>
        </div>
        <TradeHistogram trades={selectedResult.trades} mode={histogramMode}/>
      </div>
    </div>
  );
}

export default TradeAnalyticsTab;
