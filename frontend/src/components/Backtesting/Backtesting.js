import { useEffect, useState, useMemo } from "react";
import Select from "react-select";
import Chart from "../Dashboard/chart/Chart";
import { backtestSMA } from "../../utils/backtest";
import { OverviewTab } from "./tabs/OverviewTab";
import { RiskExposureTab } from "./tabs/RiskExposureTab";
import { TradeAnalyticsTab } from "./tabs/TradeAnalyticsTab";


function Backtesting() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [shortPeriod, setShortPeriod] = useState(20);
  const [longPeriod, setLongPeriod] = useState(50);
  const [backtestResult, setBacktestResult] = useState(null);
  const [strategyType, setStrategyType] = useState(null);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const strategyTypeOptions = useMemo(
    () => [
      { value: "Moving average crossover", label: "Moving Average Crossover" },
    ],
    []
  );

  // get available ticker symbols from backend
  useEffect(() => {
    fetch("http://localhost:8000/api/symbols")
      .then((res) => res.json())
      .then((data) => {
        setSymbols(data.map((s) => ({ value: s, label: s })));
        setSelectedSymbol({ value: data[0], label: data[0] });
      });

    setStrategyType(strategyTypeOptions[0]);

    fetch("http://localhost:8000/api/ohlcv/SPY?limit=500")
      .then((res) => res.json())
      .then((data) => {
        setBenchmarkData(data)
      });
  }, [strategyTypeOptions]);

  const runBacktest = async () => {
    if (!selectedSymbol) return;
    const res = await fetch(
      `http://localhost:8000/api/ohlcv/${selectedSymbol?.value}?limit=500`
    );
    const data = await res.json();
    const result = backtestSMA(data, shortPeriod, longPeriod, 10000);
    setBacktestResult(result);
    setActiveTab("overview");
  };

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
            value={selectedSymbol}
            onChange={setSelectedSymbol}
            isSearchable
            placeholder="Select a ticker"
            menuPortalTarget={document.body}
            styles={{
              menuPortal: (base) => ({ ...base, zIndex: 9999 }),
            }}
          />
        </div>

        {/* Parameters Card */}
        <div className="bg-white shadow rounded-xl p-4 col-span-1 md:col-span-2">
          <h3 className="text-lg font-semibold mb-3">Parameters</h3>
          <div className="flex flex-wrap gap-6 items-center">
            <div>
              <label className="block text-sm text-gray-600 mb-1">
                Short SMA Period
              </label>
              <input
                type="number"
                value={shortPeriod}
                onChange={(e) => setShortPeriod(Number(e.target.value))}
                className="border p-2 rounded w-28"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                Long SMA Period
              </label>
              <input
                type="number"
                value={longPeriod}
                onChange={(e) => setLongPeriod(Number(e.target.value))}
                className="border p-2 rounded w-28"
              />
            </div>

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
          {activeTab === "overview" && <OverviewTab result={backtestResult} benchmark = {benchmarkData} />}
          {activeTab === "trade-analytics" && (
            <TradeAnalyticsTab result={backtestResult} />
          )}
          {activeTab === "risk-exposure" && (
            <RiskExposureTab result={backtestResult} />
          )}
        </div>
      )}
    </div>
  );
}

export default Backtesting;
