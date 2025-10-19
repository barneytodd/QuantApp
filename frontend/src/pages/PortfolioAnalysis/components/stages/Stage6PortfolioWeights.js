import { MenuList, Option } from "../../../../components/ui/CustomSelectComponents"
import Select from "react-select"

export default function PortfolioWeights({
  onRunPortfolioWeights,
  visible,
  setVisible,
  paramValues,
  setParamValues,
  filterResults,
  portfolioWeightsLoading,
  inputsLoading,
  hrpLoading,
  optimisationLoading,
  portfolioWeightsError,
  paramOptimisationResults,
  onSavePortfolio,
  savingPortfolio,
  savedPortfolio
}) {
  return (
    <div 
      className={`${
        filterResults ? 
          "bg-green-500 text-white" : portfolioWeightsLoading ? 
            "bg-yellow-500 text-black" : portfolioWeightsError ? 
              "bg-red-500 text-black" : "bg-white text-black"
      } shadow rounded-xl p-4 mt-6 transition-colors duration-300`}
    >
      <div
        className={`flex justify-between items-center ${
          paramOptimisationResults ? "cursor-pointer" : "cursor-not-allowed text-gray-400"
        }`}
        title={
          paramOptimisationResults
            ? ""
            : "Complete pre-screen first"
        }
        onClick={() => {
          if (paramOptimisationResults) {
            setVisible((v) => !v);
          }
        }}
      >
        <h3 className="text-lg font-semibold">Optimise Portfolio Weights</h3>
        <span>{visible ? "▲" : "▼"}</span>
      </div>

      {visible && (
        <>
          {/* Filter Inputs */}
          {(() => {
            const groupTitles = {
              inputs: "Input Calculation Parameters",
              optimisation: "Optimisation Parameters",
              other: "Other Parameters",
            };

            // Group paramValues by their `group` property
            const groupedParams = Object.entries(paramValues).reduce((acc, [key, param]) => {
              const groupKey = param.group || "other";
              if (!acc[groupKey]) acc[groupKey] = [];
              acc[groupKey].push({ ...param, name: key }); // attach original key as `name`
              return acc;
            }, {});

            return Object.entries(groupedParams).map(([groupKey, paramsInGroup]) => (
              <div key={groupKey} className="mb-6">
                <h4 className="text-md font-semibold mb-2">{groupTitles[groupKey] || groupKey}</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {paramsInGroup.map((param) => (
                    <div key={param.name} className="flex items-center gap-2">
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
                              [param.name]: { ...prev[param.name], value: selected.map((s) => s.value) },
                            }))
                          }
                          closeMenuOnSelect={false}
                          hideSelectedOptions={false}
                          components={{ Option, MenuList }}
                          className="w-full"
                        />
                      ) : (
                        <input
                          type={param.type}
                          value={param.value ?? ""}
                          onChange={(e) =>
                            setParamValues((prev) => ({
                              ...prev,
                              [param.name]: { ...prev[param.name], value: e.target.value },
                            }))
                          }
                          onBlur={(e) =>
                            setParamValues((prev) => ({
                              ...prev,
                              [param.name]: {
                                ...prev[param.name],
                                value: param.type === "number" ? Number(e.target.value) || 0 : e.target.value,
                              },
                            }))
                          }
                          className={`border p-1 rounded w-full ${filterResults ? "bg-white text-black" : "bg-white text-black"}`}
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ));
          })()}

          {/* Filter Button */}
          <div className="flex justify-start gap-3 mt-5">
            <button
              onClick={onRunPortfolioWeights}
              className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {
                inputsLoading 
                  ? "Calculating inputs ..." : hrpLoading
                  ? "Running HRP allocation ..." : optimisationLoading
                  ? "Optimising Weights ..." : portfolioWeightsLoading
                  ? "Optimising ..." : filterResults 
                  ? "Completed Optimisation" : "Optimise Weights"
              }
            </button>
          </div>

          
          {/* Filter Results */}
          {filterResults != null && (
            <div className="mt-4 text-lg font-medium">
              Optimised Portfolio: {Object.entries(filterResults).map(([key, value]) => (
                <div key={key}>
                  <strong>{key}:</strong> {JSON.stringify(value)}
                </div>
              ))}
            </div>
          )}

          {/* Save Portfolio Button */}
          {filterResults && onSavePortfolio && (
            <div className="flex justify-start gap-3 mt-2">
              <button
                onClick={() => onSavePortfolio(filterResults)}
                className="px-4 py-2 rounded-lg bg-green-500 text-white hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {savingPortfolio ? "Saving ..." : savedPortfolio ? "Saved" : "Save Portfolio"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
