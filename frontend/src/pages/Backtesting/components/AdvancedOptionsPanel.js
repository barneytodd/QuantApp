import { useState } from "react";

export default function AdvancedOptionsPanel({
  isOpen,
  onClose,
  advancedParams,
  setAdvancedParams,
}) {
  // Group parameters by `param.group`
  const groupedParams = Object.entries(advancedParams).reduce((acc, [paramName, param]) => {
    const group = param.group || "Other"; // fallback group
    if (!acc[group]) acc[group] = {};
    if (!acc[group][paramName]) acc[group][paramName] = param;
    return acc;
  }, {});

  // State to track which groups are expanded
  const [expandedGroups, setExpandedGroups] = useState(
    Object.keys(groupedParams).reduce((acc, group) => {
      acc[group] = false; // default all expanded
      return acc;
    }, {})
  );

  const toggleGroup = (groupName) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  if (!isOpen) return null; // don't render when closed

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-30"
        onClick={onClose}
      />

      {/* Panel */}
      <div
        className={`ml-auto h-full w-96 bg-white shadow-xl p-6 overflow-y-auto transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
        onClick={(e) => e.stopPropagation()} // prevent closing when clicking inside
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Advanced Options</h3>
          <button
            onClick={onClose}
            className="text-gray-600 hover:text-gray-900 text-2xl"
          >
            &times;
          </button>
        </div>

        <div className="space-y-4">
          {Object.entries(groupedParams).map(([groupName, params]) => (
            <div key={groupName}>
              {/* Group header with toggle */}
              <div
                className="flex justify-between items-center cursor-pointer bg-gray-100 p-2 rounded"
                onClick={() => toggleGroup(groupName)}
              >
                <h4 className="font-semibold">{groupName}</h4>
                <span>{expandedGroups[groupName] ? "▼" : "►"}</span>
              </div>

              {/* Parameters in this group */}
              {expandedGroups[groupName] && (
                <div className="space-y-4">
                  {Object.entries(params).map(([paramName, param]) => (
                    <div key={paramName}>

                      {/* Tooltip container */}
                      <div className="relative group">
                        <span className="block text-sm font-medium cursor-pointer">{param.label}</span>
                        
                        {/* Tooltip text */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-40 bg-gray-800 text-white text-sm p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-pre-line">
                          {param.info}
                        </div>
                      </div>

                      <input
                        type={param.type}
                        value={advancedParams[paramName].value ?? ""}
                        onChange={(e) =>
                          setAdvancedParams((prev) => ({
                            ...prev,
                            [paramName]: { ...prev[paramName], value: e.target.value },
                          }))
                        }
                        onBlur={(e) =>
                          setAdvancedParams((prev) => ({
                            ...prev,
                            [paramName]: {
                              ...prev[paramName],
                              value:
                                param.type === "number"
                                  ? Number(e.target.value) || 0
                                  : e.target.value,
                            },
                          }))
                        }
                        className="border p-2 rounded w-full"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
