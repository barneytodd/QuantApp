import { useEffect, useState, useMemo } from "react";
import Select from "react-select";
import { strategies } from "./strategies/strategyRegistry";
import { OverviewTab } from "./tabs/OverviewTab";
import { RiskExposureTab } from "./tabs/RiskExposureTab";
import { TradeAnalyticsTab } from "./tabs/TradeAnalyticsTab";
import { Option, MenuList } from "../../components/ui/CustomSelectComponents"


function Backtesting() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [backtestResult, setBacktestResult] = useState([]);
  const [strategyType, setStrategyType] = useState(null);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [activeTab, setActiveTab] = useState(null);
  const [params, setParams] = useState({});
  const [pairCandidates, setPairCandidates] = useState([]);  
  const [selectedPairs, setSelectedPairs] = useState([]);    
  const [pairSectionVisible, setPairSectionVisible] = useState(true); 

  const strategyTypeOptions = useMemo(
    () =>
      Object.entries(strategies).map(([key, strat]) => ({
        value: key,
        label: strat.label,
      })),
    []
  );

  // get available ticker symbols and benchmark data from backend
  useEffect(() => {
    fetch("http://localhost:8000/api/symbols/db_symbols")
      .then((res) => res.json())
      .then((data) => {
        setSymbols(data
          .filter((s) => s !== "SPY")
          .map((s) => ({ value: s, label: s })));
      });

    fetch("http://localhost:8000/api/data/ohlcv/SPY?limit=500")
      .then((res) => res.json())
      .then((data) => {
        setBenchmarkData(data)
      });

  }, []);

  // set default strategy type
  useEffect(() => {
    setStrategyType(strategyTypeOptions[0]);
  }, [strategyTypeOptions])

  // set default parameters for selected strategy type
  useEffect(() => {
    if (strategyType) {
      const defaults = Object.fromEntries(
        strategies[strategyType.value].params.map(p => [p.name, p.default])
      );
      setParams(defaults);
    }
  }, [strategyType]);

  const selectPairs = async () => {
    if (selectedSymbols.length < 2) {
      alert("Select at least two symbols to generate pairs.");
      return;
    }

    const symbolList = selectedSymbols.map(s => s.value);

    try {
      const res = await fetch("http://localhost:8000/api/pairs/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbols: symbolList,
          w_corr: 0.5,
          w_coint: 0.5
        })
      });

      const data = await res.json();
      console.log("all", data.all_pairs, "selected", data.selected_pairs)
      setPairCandidates(data.all_pairs);
      setSelectedPairs(data.selected_pairs); // default selection from backend
      setPairSectionVisible(false);           // show the pair section
    } catch (err) {
      console.error("Failed to select pairs", err);
      alert("Failed to fetch pair analysis.");
    }
  };


  // execute backtest logic when 'run backtest' button is pressed
  const runBacktest = async () => {
    if (selectedSymbols.length === 0 || !strategyType) return;

    // Prepare payload for backend
    const payload = {
      strategy: strategyType.value,
      symbols: selectedSymbols.map(s => s.value),  // just send symbols
      params,
      initialCapital: 10000,
      pairs: strategyType.value === "pairs_trading" ? selectedPairs : undefined,
    };

    console.log(payload);

    try {
      const res = await fetch("http://localhost:8000/api/strategies/backtest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Backtest failed");

      const results = await res.json();

      setBacktestResult(results);        // individual + combined
      setActiveTab("overview");          // default to overview tab
    } catch (err) {
      console.error("Backtest error:", err);
      alert("Backtest failed. See console for details.");
    }
  };
  
  // run parameter optimisation logic (currently just a placeholder)
  const optimiseParameters = async () => {
    return;
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
              {/* Only show Select Pairs button for Pairs Trading */}
              {strategyType?.value === "pairs_trading" && (
                <button
                  onClick={selectPairs}
                  className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  Select Pairs
                </button>
              )}

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
          
      {/* PAIR SELECTION TABLE */}
      {strategyType?.value === "pairs_trading" && pairCandidates.length > 0 && (
        <div className="bg-white shadow rounded-xl p-4 mt-6">
          <div
            className="flex justify-between items-center cursor-pointer"
            onClick={() => setPairSectionVisible((v) => !v)}
          >
            <h3 className="text-lg font-semibold">Pair Selection</h3>
            <span>{pairSectionVisible ? "▲" : "▼"}</span>
          </div>

          {pairSectionVisible && (
            <table className="w-full mt-4 border-collapse border border-gray-300">
              <thead>
                <tr>
                  <th className="border px-2 py-1">Select</th>
                  <th className="border px-2 py-1">Stock 1</th>
                  <th className="border px-2 py-1">Stock 2</th>
                  <th className="border px-2 py-1">Score</th>
                  <th className="border px-2 py-1">Correlation</th>
                  <th className="border px-2 py-1">Cointegration p-value</th>
                </tr>
              </thead>
              <tbody>
                {pairCandidates.map((pair) => {
                  const isSelected = selectedPairs.some(
                    (p) =>
                      p.stock1 === pair.stock1 && p.stock2 === pair.stock2
                  );
                  return (
                    <tr key={`${pair.stock1}-${pair.stock2}`}>
                      <td className="border px-2 py-1">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedPairs((prev) => [...prev, pair]);
                            } else {
                              setSelectedPairs((prev) =>
                                prev.filter(
                                  (p) =>
                                    !(
                                      p.stock1 === pair.stock1 &&
                                      p.stock2 === pair.stock2
                                    )
                                )
                              );
                            }
                          }}
                        />
                      </td>
                      <td className="border px-2 py-1">{pair.stock1}</td>
                      <td className="border px-2 py-1">{pair.stock2}</td>
                      <td className="border px-2 py-1">
                        {pair.score.toFixed(3)}
                      </td>
                      <td className="border px-2 py-1">
                        {pair.corr.toFixed(3)}
                      </td>
                      <td className="border px-2 py-1">
                        {pair.p_value.toFixed(4)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      )}

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
