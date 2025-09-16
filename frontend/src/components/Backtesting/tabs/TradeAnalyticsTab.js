import TradeHistogram from "../charts/TradeHistogram";

export function TradeAnalyticsTab({ result }) {
  return (
    <div className="space-y-4">
      {/* Trade stats summary */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Trades</p>
          <p className="text-lg font-bold">{result.tradeStats.numTrades}</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Win Rate</p>
          <p className="text-lg font-bold">{result.tradeStats.winRate.toFixed(1)}%</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Profit Factor</p>
          <p className="text-lg font-bold">{result.tradeStats.profitFactor.toFixed(2)}</p>
        </div>
      </div>
      
      {/* Trade table */}
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="font-bold mb-2">Trade History</h3>
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Entry</th>
              <th className="text-left p-2">Exit</th>
              <th className="text-left p-2">Entry Px</th>
              <th className="text-left p-2">Exit Px</th>
              <th className="text-left p-2">PnL ($)</th>
              <th className="text-left p-2">Return %</th>
            </tr>
          </thead>
          <tbody>
            {result.trades.map((t, i) => (
              <tr key={i} className="border-b">
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

      {/* Trade PnL Distribution */}
      <div className="bg-white p-4 shadow rounded">
        <h3 className="font-bold mb-2">Trade PnL Distribution</h3>
        <TradeHistogram trades={result.trades}/>
      </div>
    </div>
  );
}

export default TradeAnalyticsTab;
