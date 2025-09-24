export default function OptimiserPanel({ isOpen, onClose, onRunOptimisation }) {
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

      {/* Optimiser settings placeholder */}
      <p className="text-gray-600 mb-6">
        Configure optimisation settings, folds, and objectives here.
      </p>

      <button
        onClick={onRunOptimisation}
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium w-full"
      >
        Run Optimisation
      </button>
    </div>
  );
}
