import { getPnlHistogram } from "../../../utils/chartCalcs";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function TradeHistogram({ trades }) {
  const histogramData = getPnlHistogram(trades);

  return (
    <div className="w-full h-80 bg-white shadow rounded-lg p-4">
      <h3 className="font-bold mb-2">Trade P&L Histogram</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={histogramData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="bin" tickLine={false} axisLine={false}  tickFormatter={(value) => `$${Math.round(value)}`} />
          <YAxis allowDecimals={false} tickLine={false} axisLine={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
