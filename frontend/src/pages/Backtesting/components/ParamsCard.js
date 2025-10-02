export default function ParamsCard({
  basicParams,
  setBasicParams,
  strategyType,
  onSelectPairs,
  pairsLoading,
  pairsError,
  onOpenAdvanced,
  onOpenOptimiser,
  onRunBacktest,
  backtestLoading,
  selectedSymbols,
  selectedPairs,
  optimError,
  optimLoading
}) {
  return (
    <div className="bg-white shadow rounded-xl p-4 col-span-1 md:col-span-2">
      <h3 className="text-lg font-semibold mb-3">Parameters</h3>
      <div className="flex flex-wrap gap-6 items-center">
        {strategyType &&
          Object.entries(basicParams).map(([key, param]) => (
            <div key={key} className="flex items-center gap-2">
              

              {/* Tooltip container */}
              <div className="relative group">
                <span className="text-black-500 cursor-pointer">{param.label}:</span>
                
                {/* Tooltip text */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-40 bg-gray-800 text-white text-sm p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-pre-line">
                  {param.info}
                </div>
              </div>

              <input
                type={param.type}
                value={param.value ?? ""}
                onChange={(e) =>
                  setBasicParams((prev) => ({
                    ...prev,
                    [key]: { ...prev[key], value: e.target.value },
                  }))
                }
                onBlur={(e) =>
                  setBasicParams((prev) => ({
                    ...prev,
                    [key]: { ...prev[key], value: Number(e.target.value) || 0 },
                  }))
                }
                className="border p-1 rounded"
              />
            </div>
          ))}

        <div className="flex gap-3 mt-5">
            {strategyType?.value === "pairs_trading" && (
                <>
                    <button
                    onClick={onSelectPairs}
                    disabled={pairsLoading}
                    className={`px-4 py-2 rounded-lg text-white ${pairsLoading ? "bg-gray-400" : "bg-green-500 hover:bg-green-600"}`}
                    >
                    {pairsLoading ? "Selecting..." : "Select Pairs"}
                    </button>

                    {pairsError && (
                    <p className="text-red-500 mt-2">{pairsError}</p>
                    )}
                </>
            )}

          <button
            onClick={onOpenAdvanced}
            className="bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-lg text-sm font-medium"
          >
            Advanced Options
          </button>

          <button
            onClick={onOpenOptimiser}
            disabled={
              optimLoading || 
              selectedSymbols.length === 0 || 
              (strategyType?.value === "pairs_trading" && selectedPairs.length === 0)
            }
            className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Optimise Parameters
          </button>

          <button
            onClick={onRunBacktest}
            disabled={
              backtestLoading || 
              selectedSymbols.length === 0 || 
              (strategyType?.value === "pairs_trading" && selectedPairs.length === 0)
            }
            className={"px-4 py-2 rounded-lg text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"}
          >
            {backtestLoading ? "Running..." : "Run Backtest"}
          </button>
        </div>
      </div>
    </div>
  );
}
