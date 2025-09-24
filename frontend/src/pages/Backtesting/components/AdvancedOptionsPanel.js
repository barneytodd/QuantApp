export default function AdvancedOptionsPanel({
  isOpen,
  onClose,
  advancedParams,
  setAdvancedParams,
}) {
  return (
    <div
      className={`fixed top-0 right-0 h-full w-96 bg-white shadow-xl z-50 p-6 overflow-y-auto transform transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
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
        {Object.entries(advancedParams).map(([key, param]) => (
          <div key={key}>
            <label className="block text-sm font-medium">{param.label}</label>
            <input
              type={param.type}
              value={param.value}
              onChange={(e) =>
                setAdvancedParams((prev) => ({
                  ...prev,
                  [key]: { ...prev[key], value: e.target.value },
                }))
              }
              onBlur={(e) =>
                setAdvancedParams((prev) => ({
                  ...prev,
                  [key]: {
                    ...prev[key],
                    value: param.type === "number" ? Number(e.target.value) || 0 : e.target.value,
                  },
                }))
              }
              className="border p-2 rounded w-full"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
