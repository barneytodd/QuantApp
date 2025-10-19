import Select from "react-select";

export default function SingleSelect({ currentValue, setCurrentValue, options, title, placeholder }) {
  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <Select
        options={options}
        value={currentValue}
        onChange={setCurrentValue}
        isSearchable
        placeholder={placeholder}
        menuPortalTarget={document.body}
        styles={{ menuPortal: (base) => ({ ...base, zIndex: 9999 }) }}
      />
    </div>
  );
}
