import { useEffect, useState, useMemo } from "react";
import Select, { components } from "react-select";
import { strategies } from "./strategies/strategyRegistry";
import { OverviewTab } from "./tabs/OverviewTab";
import { RiskExposureTab } from "./tabs/RiskExposureTab";
import { TradeAnalyticsTab } from "./tabs/TradeAnalyticsTab";
import { combineResults } from "./backtestEngine";


function Backtesting() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [backtestResult, setBacktestResult] = useState([]);
  const [strategyType, setStrategyType] = useState(null);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [activeTab, setActiveTab] = useState(null);
  const [params, setParams] = useState({});

  const strategyTypeOptions = useMemo(
    () =>
      Object.entries(strategies).map(([key, strat]) => ({
        value: key,
        label: strat.label,
      })),
    []
  );

  // get available ticker symbols from backend
  useEffect(() => {
    fetch("http://localhost:8000/api/symbols")
      .then((res) => res.json())
      .then((data) => {
        setSymbols(data
          .filter((s) => s !== "SPY")
          .map((s) => ({ value: s, label: s })));
      });

    setStrategyType(strategyTypeOptions[0]);

    fetch("http://localhost:8000/api/ohlcv/SPY?limit=500")
      .then((res) => res.json())
      .then((data) => {
        setBenchmarkData(data)
      });
  }, [strategyTypeOptions]);

  useEffect(() => {
    if (strategyType) {
      const defaults = Object.fromEntries(
        strategies[strategyType.value].params.map(p => [p.name, p.default])
      );
      setParams(defaults);
    }
  }, [strategyType]);

  const runBacktest = async () => {
    if (selectedSymbols.length === 0 || !strategyType) return;
    let results = [];
    for (let i=0; i<selectedSymbols.length; i++) {
      const res = await fetch(
        `http://localhost:8000/api/ohlcv/${selectedSymbols[i]?.value}?limit=500`
      );
      const data = await res.json();

      const strategy = strategies[strategyType.value].run;
      const result = await strategy(data, params, 10000/selectedSymbols.length); 
      results.push(result);
    }
    results.push(combineResults(results));
    console.log("results", results)
    setBacktestResult([...results]);
    console.log("back", backtestResult)

    setActiveTab("overview");
  };
  
  useEffect(() => {
    console.log("backtestResult updated:", backtestResult);
  }, [backtestResult]);

  const optimiseParameters = async () => {
    return;
  };

  // Option with a readonly checkbox (prevents React warning)
  const Option = (props) => (
    <components.Option {...props}>
      <input
        type="checkbox"
        checked={props.isSelected}
        readOnly
        style={{ marginRight: 8 }}
      />
      <span>{props.label}</span>
    </components.Option>
  );

  // MenuList that adds a Select all / Clear all control at the top
  const MenuList = (props) => {
    const { options } = props; // all options shown in this menu
    const { value = [], onChange } = props.selectProps; // selected options array and onChange

    const allSelected = value.length === options.length && options.length > 0;

    const toggleSelectAll = (e) => {
      // prevent the menu from closing and the click from bubbling
      e.preventDefault();
      e.stopPropagation();

      if (allSelected) {
        // clear selection
        onChange([], { action: "clear" });
      } else {
        // select all options (pass the same option objects the Select is using)
        onChange(options, { action: "select-option" });
      }
    };

    return (
      <components.MenuList {...props}>
        <div
          style={{
            padding: 8,
            borderBottom: "1px solid #eee",
            // sticky header while scrolling
            position: "sticky",
            top: 0,
            background: "white",
            zIndex: 1,
          }}
        >
          <button
            type="button"
            // use onMouseDown to prevent the menu from losing focus and closing
            onMouseDown={(e) => toggleSelectAll(e)}
            style={{
              cursor: "pointer",
              border: "none",
              background: "transparent",
              padding: 0,
              fontWeight: 600,
              color: "#2563eb",
            }}
          >
            {allSelected ? "Clear all" : "Select all"}
          </button>
        </div>

        {props.children}
      </components.MenuList>
    );
  };

  return (
    <div className="space-y-6">
      {/* INPUT SECTION */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strategy Card */}
        <div className="bg-white shadow rounded-xl p-4">
          <h3 className="text-lg font-semibold mb-3">Trading Strategy</h3>
          <Select
            options={strategyTypeOptions}
            value={strategyType}
            onChange={setStrategyType}
            isSearchable
            placeholder="Select a strategy"
            menuPortalTarget={document.body}
            styles={{
              menuPortal: (base) => ({ ...base, zIndex: 9999 }),
            }}
          />
        </div>

        {/* Symbol Card */}
        <div className="bg-white shadow rounded-xl p-4">
          <h3 className="text-lg font-semibold mb-3">Symbol</h3>
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
            styles={{
              menuPortal: (base) => ({ ...base, zIndex: 9999 }),
            }}
          />  
        </div>

        {/* Parameters Card */}
        <div className="bg-white shadow rounded-xl p-4 col-span-1 md:col-span-2">
          <h3 className="text-lg font-semibold mb-3">Parameters</h3>
          <div className="flex flex-wrap gap-6 items-center">
            {strategyType && strategies[strategyType.value].params.map((param) => (
              <div key={param.name} className="flex items-center gap-2">
                <span>{param.label}:</span>
                <input
                  type={param.type}
                  value={params[param.name]}
                  onChange={(e) =>
                    setParams((prev) => ({ ...prev, [param.name]: Number(e.target.value) }))
                  }
                  className="border p-1 rounded"
                />
              </div>
            ))}


            <div className="flex gap-3 mt-5">
              <button
                onClick={optimiseParameters}
                className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm font-medium"
              >
                Optimise
              </button>
              <button
                onClick={runBacktest}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                Run Backtest
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* TABS SECTION */}
      {backtestResult && (
        <div className="space-y-4">
          {/* Tab navigation */}
          <div className="flex gap-4 border-b">
            {["overview", "trade-analytics", "risk-exposure"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 -mb-px transition ${
                  activeTab === tab
                    ? "border-b-2 border-blue-500 font-semibold"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab
                  .replace("-", " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </button>
            ))}
          </div>

          {/* Content */}
          {activeTab === "overview" && <OverviewTab results={backtestResult} benchmark = {benchmarkData} />}
          {activeTab === "trade-analytics" && (
            <TradeAnalyticsTab results={backtestResult} />
          )}
          {activeTab === "risk-exposure" && (
            <RiskExposureTab results={backtestResult} />
          )}
        </div>
      )}
    </div>
  );
}

export default Backtesting;
