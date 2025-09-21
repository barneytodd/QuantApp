import { getTradeHistogram } from "./chartCalcs";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

const colorPalette = [
  "#2563eb", // blue
  "#f97316", // orange
  "#16a34a", // green
  "#db2777", // pink
  "#eab308", // yellow
  "#8b5cf6", // purple
  "#14b8a6", // teal
];

// build trade histogram
export default function TradeHistogram({ trades, mode }) {
  const histogramData = getTradeHistogram(trades, mode);

  const symbols = Array.from(new Set(trades.map((t) => t.symbol)));

  return (
    <div className="w-full h-80 bg-white shadow rounded-lg p-4">
      <h3 className="font-bold mb-2">{mode} Histogram</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={histogramData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bin" />
          <YAxis />
          <Tooltip />
          <Legend />
          {symbols.map((sym, i) => (
            <Bar
              key={sym}
              dataKey={sym}
              stackId="pnl"
              fill={colorPalette[i % colorPalette.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
