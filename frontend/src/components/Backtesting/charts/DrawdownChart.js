import { computeDrawdowns } from "./chartCalcs";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function DrawdownChart({ equityCurve }) {
  const drawdownData = computeDrawdowns(equityCurve);

  return (
    <div className="w-full h-80 bg-white shadow rounded-lg p-4">
      <h3 className="font-bold mb-2">Drawdown</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={drawdownData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tickLine={false} axisLine={false} />
          <YAxis
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            formatter={(value) => `${(value * 100).toFixed(2)}%`}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="drawdown"
            stroke="#dc2626"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
