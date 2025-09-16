import EquityChart from "../charts/EquityChart";
import { mapBenchmark } from "../../../utils/chartCalcs";

export function OverviewTab({ result, benchmark }) {

    return (
        <div className="space-y-4">
        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 shadow rounded">
            <p className="text-sm text-gray-500">Final Capital</p>
            <p className="text-lg font-bold">${result.finalCapital.toFixed(2)}</p>
            </div>
            <div className="bg-white p-4 shadow rounded">
            <p className="text-sm text-gray-500">Return %</p>
            <p className="text-lg font-bold">{result.returnPct.toFixed(2)}%</p>
            </div>
            <div className="bg-white p-4 shadow rounded">
            <p className="text-sm text-gray-500">Sharpe Ratio</p>
            <p className="text-lg font-bold">{result.metrics.sharpe_ratio?.toFixed(2) ?? "-"}</p>
            </div>
            <div className="bg-white p-4 shadow rounded">
            <p className="text-sm text-gray-500">Max Drawdown</p>
            <p className="text-lg font-bold">
                {result.metrics.max_drawdown?.toFixed(2) ?? "-"}%
            </p>
            </div>
        </div>

        {/* Equity Curve */}
        <div className="bg-white p-4 shadow rounded">
            <h3 className="font-bold mb-2">Equity Curve</h3>
            <EquityChart 
                equityData={result.equityCurve} 
                benchmarkData={mapBenchmark(benchmark, result.initialCapital)}
            />
        </div>

        {/* Drawdown Curve (placeholder) */}
        <div className="bg-white p-4 shadow rounded">
            <h3 className="font-bold mb-2">Drawdown Curve</h3>
            <p className="text-gray-500">Coming soon: drawdown chart…</p>
        </div>
        </div>
    );
    }

    export default OverviewTab;
