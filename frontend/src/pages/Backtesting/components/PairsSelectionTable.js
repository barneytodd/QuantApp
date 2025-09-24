export default function PairsSelectionTable({
  pairCandidates,
  selectedPairs,
  setSelectedPairs,
  visible,
  setVisible,
}) {
  if (!pairCandidates.length) return null;

  return (
    <div className="bg-white shadow rounded-xl p-4 mt-6">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setVisible((v) => !v)}
      >
        <h3 className="text-lg font-semibold">Pair Selection</h3>
        <span>{visible ? "▲" : "▼"}</span>
      </div>

      {visible && (
        <table className="w-full mt-4 border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border px-2 py-1">Select</th>
              <th className="border px-2 py-1">Stock 1</th>
              <th className="border px-2 py-1">Stock 2</th>
              <th className="border px-2 py-1">Score</th>
              <th className="border px-2 py-1">Correlation</th>
              <th className="border px-2 py-1">Cointegration p-value</th>
            </tr>
          </thead>
          <tbody>
            {pairCandidates.map((pair) => {
              const isSelected = selectedPairs.some(
                (p) => p.stock1 === pair.stock1 && p.stock2 === pair.stock2
              );
              return (
                <tr key={`${pair.stock1}-${pair.stock2}`}>
                  <td className="border px-2 py-1">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedPairs((prev) => [...prev, pair]);
                        } else {
                          setSelectedPairs((prev) =>
                            prev.filter(
                              (p) =>
                                !(
                                  p.stock1 === pair.stock1 &&
                                  p.stock2 === pair.stock2
                                )
                            )
                          );
                        }
                      }}
                    />
                  </td>
                  <td className="border px-2 py-1">{pair.stock1}</td>
                  <td className="border px-2 py-1">{pair.stock2}</td>
                  <td className="border px-2 py-1">{pair.score.toFixed(3)}</td>
                  <td className="border px-2 py-1">{pair.corr.toFixed(3)}</td>
                  <td className="border px-2 py-1">{pair.p_value.toFixed(4)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
