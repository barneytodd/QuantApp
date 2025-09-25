export default function OptimiserPanel({ 
  isOpen, 
  onClose, 
  optimisationParams, 
  setOptimisationParams, 
  onRunOptimisation 
}) {
  return (
    <div
      className={`fixed top-0 right-0 h-full w-96 bg-white shadow-xl z-50 p-6 overflow-y-auto transform transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Parameter Optimiser</h3>
        <button
          onClick={onClose}
          className="text-gray-600 hover:text-gray-900 text-2xl"
        >
          &times;
        </button>
      </div>

      {/* Optimiser settings */}
      <div className="space-y-4">
        {Object.entries(optimisationParams).map(([key, param]) => (
          <div key={key}>
            <label className="block text-sm font-medium">{param.label}</label>
            <input
              type={param.type}
              value={param.value}
              onChange={(e) =>
                setOptimisationParams((prev) => ({
                  ...prev,
                  [key]: { ...prev[key], value: e.target.value },
                }))
              }
              onBlur={(e) =>
                setOptimisationParams((prev) => ({
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
      
      <div>
        <button
          onClick={onRunOptimisation}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium w-full"
        >
          Run Optimisation
        </button>
      </div>
    </div>
  );
}
