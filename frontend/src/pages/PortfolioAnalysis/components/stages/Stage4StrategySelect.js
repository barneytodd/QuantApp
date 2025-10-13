import { MenuList, Option } from "../../../../components/ui/CustomSelectComponents"
import Select from "react-select"

export default function StrategySelector({
  paramValues,
  setParamValues,
  onRunStrategySelect,
  visible,
  setVisible,
  filterResults,
  strategySelectLoading,
  strategySelectError,
  prelimBacktestResults,
  strategyType,
  uploadComplete,
  progress
}) {
  return (
    <div 
      className={`${
        filterResults ? 
          "bg-green-500 text-white" : strategySelectLoading ? 
            "bg-yellow-500 text-black" : strategySelectError ? 
              "bg-red-500 text-black" : "bg-white text-black"
      } shadow rounded-xl p-4 mt-6 transition-colors duration-300`}
    >
      <div
        className={`flex justify-between items-center ${
          prelimBacktestResults ? "cursor-pointer" : "cursor-not-allowed text-gray-400"
        }`}
        title={
          prelimBacktestResults
            ? ""
            : "Complete pre-screen first"
        }
        onClick={() => {
          if (prelimBacktestResults) {
            setVisible((v) => !v);
          }
        }}
      >
        <h3 className="text-lg font-semibold">Select Best Strategies</h3>
        <span>{visible ? "▲" : "▼"}</span>
      </div>

      {visible && (
        <>
          {/* Filter Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
            {Object.entries(paramValues).map(([key, param]) => (
              <div key={key} className="flex items-center gap-2">
                {/* Tooltip */}
                <div className="relative group">
                  <span className="cursor-pointer">{param.label}:</span>
                  {param.info && (
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-40 bg-gray-800 text-white text-sm p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-pre-line">
                      {param.info}
                    </div>
                  )}
                </div>

                {param.type === "categorical" ? (
                    <Select
                        isMulti
                        options={(param.options || []).map((opt) => ({ label: opt, value: opt }))}
                        value={(param.value || []).map((val) => ({ label: val, value: val }))}
                        onChange={(selected) =>
                        setParamValues((prev) => ({
                            ...prev,
                            [key]: { ...prev[key], value: selected.map((s) => s.value) },
                        }))
                        }
                        closeMenuOnSelect={false}
                        hideSelectedOptions={false}
                        components={{ Option, MenuList }}
                        className="w-full"
                        styles={{
                            multiValue: (base) => ({
                            ...base,
                            maxWidth: '100%', // prevent wrapping or overflow
                            }),
                            valueContainer: (base) => ({
                            ...base,
                            maxHeight: '100px', // set max height
                            overflowY: 'auto',  // enable scrolling
                            color: 'black',
                            }),
                            input: (base) => ({
                                ...base,
                                color: 'black',   // input text
                            }),
                            option: (base, state) => ({
                                ...base,
                                color: 'black',    // options in dropdown
                                backgroundColor: state.isSelected ? '#e5e7eb' : 'white',
                            }),
                            menu: (base) => ({
                            ...base,
                            zIndex: 9999, // ensure it shows on top
                            }),
                        }}
                    />
                ) : (
                    <input
                    type={param.type}
                    value={param.value ?? ""}
                    onChange={(e) =>
                        setParamValues((prev) => ({
                        ...prev,
                        [key]: { ...prev[key], value: e.target.value },
                        }))
                    }
                    onBlur={(e) =>
                        setParamValues((prev) => ({
                        ...prev,
                        [key]: {
                            ...prev[key],
                            value:
                            param.type === "number"
                                ? Number(e.target.value) || 0
                                : e.target.value,
                        },
                        }))
                    }
                    className={`border p-1 rounded w-full ${filterResults ? "bg-white text-black" : "bg-white text-black"}`}
                    />
                )}
              </div>
            ))}
          </div>

          {/* Filter Button */}
          <div className="flex justify-start gap-3 mt-5">
            <button
              onClick={onRunStrategySelect}
              disabled={strategyType?.value !== "custom"}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {strategySelectLoading ? "Running Backtests ..." : filterResults ? "Selected Strategies" : !uploadComplete ? "Loading Data ..." : "Select Strategies"}
            </button>
          </div>

          {/* Filter Results */}
          {filterResults != null && (
            <div className="mt-4 text-lg font-medium">
              Filtered to {Object.keys(filterResults).length} results:
            </div>
          )}

          {progress && !filterResults && (
            <div className="mt-4">
              {/* Overall Progress */}
              {typeof progress.overall_progress === "number" && (
                <div className="mb-4">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                    <span className="text-sm font-medium text-gray-700">
                      {progress.overall_progress.toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                    <div
                      className="bg-blue-500 h-4 rounded-full transition-all duration-500"
                      style={{ width: `${progress.overall_progress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Segment Progress Bars */}
              {progress.segments && Object.keys(progress.segments).length > 0 && (
                <div className="space-y-2">
                  {Object.entries(progress.segments).map(([key, seg]) => (
                    <div key={key}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Segment {key}</span>
                        <span className="text-sm font-medium">
                          {typeof seg.progress_pct === "number" ? seg.progress_pct.toFixed(2) : 0}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-green-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${seg.progress_pct || 0}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
