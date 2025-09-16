import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

export default function EquityChart({ equityData, benchmarkData }) {
  // Merge equity and benchmark for plotting
  const merged = equityData.map((d, i) => ({
    date: d.date,
    equity: d.value,
    benchmark: benchmarkData?.[i]?.value ?? null,
  }));

  return (
    <div className="w-full h-80 bg-white shadow rounded-lg p-4">
      <h3 className="font-bold mb-2">Equity Curve vs Benchmark</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={merged}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickLine={false}
            axisLine={false}
            minTickGap={20}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `$${v.toLocaleString()}`}
          />
          <Tooltip
            formatter={(value, name) => [`$${value.toFixed(2)}`, name === "equity" ? "Equity" : "Benchmark"]}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend verticalAlign="top" />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
          />
          {benchmarkData && (
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#16a34a"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
