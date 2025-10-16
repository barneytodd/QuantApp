import { MenuList, Option } from "../../../../components/ui/CustomSelectComponents"
import Select from "react-select"

export default function ParamOptimsation({
  onRunParamOptimisation,
  visible,
  setVisible,
  paramValues,
  setParamValues,
  filterResults,
  paramOptimisationLoading,
  paramOptimisationError,
  strategySelectResults,
  progress
}) {
  return (
    <div 
      className={`${
        filterResults ? 
          "bg-green-500 text-white" : paramOptimisationLoading ? 
            "bg-yellow-500 text-black" : paramOptimisationError ? 
              "bg-red-500 text-black" : "bg-white text-black"
      } shadow rounded-xl p-4 mt-6 transition-colors duration-300`}
    >
      <div
        className={`flex justify-between items-center ${
          strategySelectResults ? "cursor-pointer" : "cursor-not-allowed text-gray-400"
        }`}
        title={
          strategySelectResults
            ? ""
            : "Complete pre-screen first"
        }
        onClick={() => {
          if (strategySelectResults) {
            setVisible((v) => !v);
          }
        }}
      >
        <h3 className="text-lg font-semibold">Optimise Parameters</h3>
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
              onClick={onRunParamOptimisation}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {paramOptimisationLoading && (Object.keys(progress).length === 0)
                ? "Loading Data ..." : paramOptimisationLoading
                ? "Optimising Params..." : filterResults 
                ? "Completed Optimisation..." : "Optimise Parameters"}
            </button>
          </div>

          {/* Filter Results */}
          {filterResults != null && (
            <div className="mt-4 text-lg font-medium">
              Filtered to {Object.keys(filterResults).length} results:
            </div>
          )}
        </>
      )}
    </div>
  );
}
