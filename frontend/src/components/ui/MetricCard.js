export default function MetricCard({ label, value, dp=2, type=null }) {
  // Format percentages if the value is a fraction
  let displayValue = "-";
  if (typeof value === "number") {
    if (type === "currency") {
      displayValue = `$${value.toFixed(dp)}`;
    } else if (type === "percentage") {
      displayValue = `${value.toFixed(dp)}%`;
    } else {
      displayValue = value.toFixed(dp);
    }
  }

  return (
    <div className="bg-white p-4 rounded-2xl shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-bold">{displayValue}</p>
    </div>
  );
}
