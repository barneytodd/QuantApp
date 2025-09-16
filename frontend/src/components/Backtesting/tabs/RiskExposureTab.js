import DrawdownChart from "../charts/DrawdownChart";

export function RiskExposureTab({ result }) {
  const { metrics } = result;

  return (
    <div className="space-y-4">
      {/* Risk metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Annualised Return</p>
          <p className="text-lg font-bold">{(metrics.mean_return * 100).toFixed(2)}%</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Volatility</p>
          <p className="text-lg font-bold">{(metrics.annualised_volatility * 100).toFixed(2)}%</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm text-gray-500">Sharpe Ratio</p>
          <p className="text-lg font-bold">{metrics.sharpe_ratio.toFixed(2)}</p>
        </div>
      </div>

      {/* Equity Curve */}
      <div className="bg-white p-4 shadow rounded">
        <h3 className="font-bold mb-2">Drawdown Chart</h3>
        <DrawdownChart equityCurve={result.equityCurve}/>
      </div>
    </div>
  );
}

export default RiskExposureTab;
