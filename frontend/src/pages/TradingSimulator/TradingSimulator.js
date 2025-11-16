import { useState, useEffect } from "react";
import { useLoadPortfolios } from "./hooks/useLoadPortfolio";
import { usePortfolioBacktest } from "./hooks/usePortfolioBacktest";
import { globalParams } from "../Backtesting/parameters/globalParams";
import { strategies } from "../Backtesting/parameters/strategyRegistry";
import { getApiUrl } from "../../utils/apiUrl";

import ParamCard from "../../components/ui/ParamCard";
import MetricCard from "../../components/ui/MetricCard";
import SingleSelect from "../../components/ui/SingleSelect";

import OverviewTab from "../Backtesting/tabs/OverviewTab";
import TradeAnalyticsTab from "../Backtesting/tabs/TradeAnalyticsTab";
import RiskExposureTab from "../Backtesting/tabs/RiskExposureTab";


export default function TradingSimulatorPage() {
  const [portfolio, setPortfolio] = useState({});
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [globParams, setGlobParams] = useState({});
  const [dataLoading, setDataLoading] = useState(false);
  const [benchmarkData, setBenchmarkData] = useState(null)

  const [activeTab, setActiveTab] = useState(null);

  const [portfolioStage, setPortfolioStage] = useState({value: "portfolioWeights", label: "Weights Applied"})
  const [filteredPortfolios, setFilteredPortfolios] = useState([]);
  const [selectedPortfolios, setSelectedPortfolios] = useState([]);
  const { availablePortfolios } = useLoadPortfolios()

  const {
    backtestResult, 
    runBacktest, 
    isLoading: backtestLoading, 
  } = usePortfolioBacktest();

  useEffect(() => {
    const portfolios = availablePortfolios.filter((p) => p.value.meta.savedFrom === portfolioStage.value)
    setFilteredPortfolios(portfolios)
  }, [portfolioStage, availablePortfolios])

  useEffect(() => {
    const globalDefaults = Object.fromEntries(
        globalParams
          .map(p => {
            const { default: value, name, ...rest } = p;
            return [name, { value, ...rest }];
          })
      );
    setGlobParams(globalDefaults)
    setStartDate(globalDefaults.startDate)
    setEndDate(globalDefaults.endDate)
  }, [])

  useEffect(() => {
    fetch(`${getApiUrl()}/api/data/ohlcv/SPY?limit=500`)
      .then((res) => res.json())
      .then((data) => setBenchmarkData(data));
  }, [backtestResult])

  const handleAddPortfolio = () => {
    if (!portfolio.value) return; // Ensure a portfolio is selected

    
    const stratParams = Object.fromEntries(
      Object.entries(portfolio.value.data).flatMap(([strat, stratResult]) => 
        Object.entries(stratResult.params).map(([param, paramValue]) => {
          const { default: value, name, ...rest } = strategies[strat].params.find(p => p.name === param)
          return [
            name, 
            { value: paramValue, ...rest }
          ]
        })
      )
    );

    const allParams = Object.fromEntries(
      Object.entries({...stratParams, ...globParams})
        .map(([k, v]) => [
            k, 
            { 
                value: k === "startDate" ? startDate.value : k === "endDate" ? endDate.value : v.value, 
                lookback: v.lookback ?? false 
            }
        ])
    );

    const newEntry = {
      portfolio: portfolio.value,
      params: allParams,
      stage: portfolio.value.meta.savedFrom,
      trainStart: portfolio.value.meta.start,
      trainEnd: portfolio.value.meta.end,
      testStart: startDate?.value,
      testEnd: endDate?.value,
    };

    setSelectedPortfolios((prev) => [...prev, newEntry]);
  };

  const handleRemovePortfolio = (index) => {
    setSelectedPortfolios(prev => prev.filter((_, idx) => idx !== index));
  };

  const handleRunBacktest = async () => {
    if (selectedPortfolios.length === 0) return;
    try {
      setDataLoading(true);
      for (const p of selectedPortfolios) {
        // Flatten symbols for this portfolio
        const syms = Object.entries(p.portfolio.data).flatMap(([strat, stratResults]) =>
          stratResults.symbols.map((s) => ({
            symbols: s.symbol.split("-"),
            strategy: strat,
            weight: s.weight,
          }))
        );

        const symbols = [...syms.flatMap((sym) => sym.symbols), "SPY"];

        // Ingest data for this portfolio
        const ingestRes = await fetch(`${getApiUrl()}/api/data/ohlcv/syncIngest/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ symbols, start: p.testStart, end: p.testEnd }),
        });
        await ingestRes.json();
      }
    } catch (err) {
      console.error(err);
      alert("Data ingestion or backtest failed");
    } finally {
      setDataLoading(false);
    }

    await runBacktest(selectedPortfolios);

  };

  useEffect(() => console.log(backtestResult), [backtestResult])

  return (
      <div className="space-y-6">
        {/* Strategy + Params */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <SingleSelect
            currentValue={portfolioStage}
            setCurrentValue={setPortfolioStage}
            options={[
              {value: "portfolioWeights", label: "Weights Applied"},
              {value: "paramOptimisation", label: "Optimised Parameters"},
              {value: "strategySelect", label: "Best Strategies Selected"}
            ]}
            title="Portfolio Stage"
            placeholder="Filter Portfolios"
          />

          <SingleSelect
            currentValue={portfolio}
            setCurrentValue={setPortfolio}
            options={filteredPortfolios}
            title="Portfolio"
            placeholder="Choose a portfolio"
          />

          <ParamCard
            param={startDate}
            setParam={setStartDate}
          />

          <ParamCard
            param={endDate}
            setParam={setEndDate}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {portfolio.value && (
            <>
              <MetricCard 
                label="Saved From"
                value={portfolio.value.meta.savedFrom}
              />

              <MetricCard 
                label="Training Start"
                value={portfolio.value.meta.start}
              />

              <MetricCard 
                label="Training End"
                value={portfolio.value.meta.end}
              />
            </>
          )}
          <button
            onClick={handleAddPortfolio}
            disabled={!portfolio.value}
            className="px-4 py-2 rounded-lg text-white bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add to Selected Portfolios
          </button>
          <div className="col-span-1 md:col-span-3 mt-4">
            {selectedPortfolios.length > 0 && (
              <div className="overflow-x-auto border rounded-lg">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2">Stage</th>
                      <th className="px-4 py-2">Train Start</th>
                      <th className="px-4 py-2">Train End</th>
                      <th className="px-4 py-2">Test Start</th>
                      <th className="px-4 py-2">Test End</th>
                      <th className="px-4 py-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPortfolios.map((p, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="px-4 py-2">{p.stage}</td>
                        <td className="px-4 py-2">{p.trainStart}</td>
                        <td className="px-4 py-2">{p.trainEnd}</td>
                        <td className="px-4 py-2">{p.testStart}</td>
                        <td className="px-4 py-2">{p.testEnd}</td>
                        <td className="px-4 py-2 text-right">
                          <button
                            onClick={() => handleRemovePortfolio(idx)}
                            className="px-2 py-1 text-white bg-red-500 rounded hover:bg-red-600"
                          >
                            X
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
          <button
            onClick={handleRunBacktest}
            disabled={
              backtestLoading || selectedPortfolios.length === 0
            }
            className={"px-4 py-2 rounded-lg text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"}
          >
            {backtestLoading ? "Running..." : dataLoading ? "Loading Data ..." : "Run Backtest"}
          </button>

        </div>
        {/* Results Tabs */}
        {backtestResult && (
          <div className="space-y-4">
            <div className="flex gap-4 border-b pb-2">
              {["Overview", "Trade Analytics", "Risk & Exposure"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-2 ${
                    activeTab === tab
                      ? "border-b-2 border-blue-500 font-semibold"
                      : "text-gray-500"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
  
            {activeTab === "Overview" && (
              <OverviewTab results={backtestResult} benchmark={benchmarkData} startDate = {startDate} showIndividual={false} extraStats={true}/>
            )}
            {activeTab === "Trade Analytics" && (
              <TradeAnalyticsTab results={backtestResult} />
            )}
            {activeTab === "Risk & Exposure" && (
              <RiskExposureTab results={backtestResult} />
            )}
          </div>
        )}
      </div>
    );
  }