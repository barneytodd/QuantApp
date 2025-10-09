export default function StrategySelection({
  visible,
  setVisible,
}) {
  return (
    <div className="bg-white shadow rounded-xl p-4 mt-6">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setVisible((v) => !v)}
      >
        <h3 className="text-lg font-semibold">Identify Best Strategies</h3>
        <span>{visible ? "▲" : "▼"}</span>
      </div>

      {visible && (
        <h4 className="text-lg font-semibold mb-3">Stage 3. Strategy Pairing & Candidate Selection</h4>
      )}
    </div>
  );
}
