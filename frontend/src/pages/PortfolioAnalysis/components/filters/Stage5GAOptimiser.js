export default function GAOptimisation({
  visible,
  setVisible,
}) {
  return (
    <div className="bg-white shadow rounded-xl p-4 mt-6">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setVisible((v) => !v)}
      >
        <h3 className="text-lg font-semibold">Build Portfolio</h3>
        <span>{visible ? "▲" : "▼"}</span>
      </div>

      {visible && (
        <h4 className="text-lg font-semibold mb-3">Stage 4. Build Optimised Portfolio</h4>
      )}
    </div>
  );
}
