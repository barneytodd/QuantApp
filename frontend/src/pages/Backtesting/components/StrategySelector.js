import Select from "react-select";

export default function StrategySelector({ strategyType, setStrategyType, options }) {
  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h3 className="text-lg font-semibold mb-3">Trading Strategy</h3>
      <Select
        options={options}
        value={strategyType}
        onChange={setStrategyType}
        isSearchable
        placeholder="Select a strategy"
        menuPortalTarget={document.body}
        styles={{ menuPortal: (base) => ({ ...base, zIndex: 9999 }) }}
      />
    </div>
  );
}
