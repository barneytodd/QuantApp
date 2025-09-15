export default function MetricCard({ label, value }) {
  // Format percentages if the value is a fraction
  const displayValue =
    typeof value === "number" && value <= 1 && value >= -1
      ? (value * 100).toFixed(2) + "%"
      : value?.toFixed?.(2) ?? "-";

  return (
    <div className="bg-white p-4 rounded-2xl shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-bold">{displayValue}</p>
    </div>
  );
}
