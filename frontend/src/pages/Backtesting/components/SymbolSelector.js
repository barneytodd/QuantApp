import Select from "react-select";
import { Option, MenuList } from "../../../components/ui/CustomSelectComponents";

export default function SymbolSelector({ symbols, selectedSymbols, setSelectedSymbols }) {
  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h3 className="text-lg font-semibold mb-3">Symbols</h3>
      <Select
        options={symbols}
        value={selectedSymbols}
        onChange={setSelectedSymbols}
        isMulti
        isSearchable
        closeMenuOnSelect={false}
        hideSelectedOptions={false}
        placeholder="Select tickers"
        menuPortalTarget={document.body}
        components={{ Option, MenuList }}
        styles={{ menuPortal: (base) => ({ ...base, zIndex: 9999 }) }}
      />
    </div>
  );
}
