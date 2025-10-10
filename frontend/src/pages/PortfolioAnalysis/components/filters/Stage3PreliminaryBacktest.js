import { MenuList, Option } from "../../../../components/ui/CustomSelectComponents"
import Select from "react-select"

export default function PreliminaryBacktest({
  filterValues,
  setFilterValues,
  onRunBacktest,
  visible,
  setVisible,
  filterResults,
  backtestLoading,
  backtestError,
  preScreenResults
}) {
  return (
    <div 
      className={`${
        filterResults ? 
          "bg-green-500 text-white" : backtestLoading ? 
            "bg-yellow-500 text-black" : backtestError ? 
              "bg-red-500 text-black" : "bg-white text-black"
      } shadow rounded-xl p-4 mt-6 transition-colors duration-300`}
    >
      <div
        className={`flex justify-between items-center ${
          preScreenResults?.length ? "cursor-pointer" : "cursor-not-allowed text-gray-400"
        }`}
        title={
          preScreenResults?.length
            ? ""
            : "Complete broad universal filter first"
        }
        onClick={() => {
          if (true) { //(preScreenResults?.length) {
            setVisible((v) => !v);
          }
        }}
      >
        <h3 className="text-lg font-semibold">Preliminary Backtest</h3>
        <span>{visible ? "▲" : "▼"}</span>
      </div>

      {visible && (
        <>
          {/* Filter Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
            {Object.entries(filterValues).map(([key, filter]) => (
              <div key={key} className="flex items-center gap-2">
                {/* Tooltip */}
                <div className="relative group">
                  <span className="cursor-pointer">{filter.label}:</span>
                  {filter.info && (
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-40 bg-gray-800 text-white text-sm p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-pre-line">
                      {filter.info}
                    </div>
                  )}
                </div>

                {filter.type === "categorical" ? (
                    <Select
                        isMulti
                        options={(filter.options || []).map((opt) => ({ label: opt, value: opt }))}
                        value={(filter.value || []).map((val) => ({ label: val, value: val }))}
                        onChange={(selected) =>
                        setFilterValues((prev) => ({
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
                    type={filter.type}
                    value={filter.value ?? ""}
                    onChange={(e) =>
                        setFilterValues((prev) => ({
                        ...prev,
                        [key]: { ...prev[key], value: e.target.value },
                        }))
                    }
                    onBlur={(e) =>
                        setFilterValues((prev) => ({
                        ...prev,
                        [key]: {
                            ...prev[key],
                            value:
                            filter.type === "number"
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
              onClick={onRunBacktest}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {backtestLoading ? "Filtering ..." : filterResults ? "Filtered" : "Filter"}
            </button>
          </div>

          {/* Filter Results */}
          {filterResults != null && (
            <div className="mt-4 text-lg font-medium">
              Filtered to {filterResults.length} results:
            </div>
          )}
        </>
      )}
    </div>
  );
}
