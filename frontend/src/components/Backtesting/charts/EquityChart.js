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

const colorPalette = [
  "#2563eb", // blue
  "#f97316", // orange
  "#16a34a", // green
  "#db2777", // pink
  "#eab308", // yellow
  "#8b5cf6", // purple
  "#14b8a6", // teal
];

// build equity chart
export default function EquityChart({ equityData, benchmarkData, highlightOverall }) {
  if (!equityData || equityData.length === 0) return null;

  // Determine the reference capital for scaling the benchmark
  const overallResult = equityData.find((r) => r.symbol === "overall");
  const refCapital = highlightOverall
    ? overallResult?.initialCapital || 10000
    : equityData[0]?.initialCapital || 10000;

  // Build list of dates
  let dates;
  if (highlightOverall) {
    dates = [
      ...new Set(equityData.flatMap((r) => r.equityCurve.map((p) => p.date))),
    ].sort();
  } else {
    dates = equityData[0].equityCurve.map((p) => p.date);
  }

  // Merge data for multiple tickers
  const mergedData = dates.map((date) => {
    const point = { date };

    equityData.forEach((r) => {
      const match = r.equityCurve.find((p) => p.date === date);
      point[r.symbol] = match ? match.value : null;
    });

    // Add benchmark scaled to the selected reference capital
    if (benchmarkData) {
      const bm = benchmarkData.find((b) => b.date === date);
      point["benchmark"] = bm ? bm.value * (refCapital / benchmarkData[0].value) : null;
    }

    return point;
  });

  return (
    <div className="w-full h-80 bg-white shadow rounded-lg p-4">
      <h3 className="font-bold mb-2">Equity Curve vs Benchmark</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={mergedData}>
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
            formatter={(value, name) => [`$${value.toFixed(2)}`, name]}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend verticalAlign="top" />

          {equityData.map((r, idx) => {
            const isOverall = r.symbol === "overall";
            let strokeOpacity = 1;
            if (highlightOverall && !isOverall) {
              strokeOpacity = 0.4; // faded for non-overall
            }
            return (
              <Line
                key={r.symbol}
                type="monotone"
                dataKey={r.symbol}
                stroke={colorPalette[idx % colorPalette.length]}
                strokeWidth={isOverall ? 3 : 2}
                dot={false}
                opacity={strokeOpacity}
              />
            );
          })}

          {benchmarkData && (
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#16a34a"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
              name="benchmark (SPY)"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
