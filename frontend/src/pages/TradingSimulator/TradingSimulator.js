import { useState, useEffect } from "react";
import { useLoadPortfolios } from "./hooks/useLoadPortfolio";
import { useBacktest } from "../Backtesting/hooks/useBacktest";
import { useSymbols } from "../Backtesting/hooks/useSymbols";
import { globalParams } from "../Backtesting/parameters/globalParams";
import { strategies } from "../Backtesting/parameters/strategyRegistry";

import ParamCard from "./components/ParamCard";
import SingleSelect from "../../components/ui/SingleSelect";


import OverviewTab from "../Backtesting/tabs/OverviewTab";
import TradeAnalyticsTab from "../Backtesting/tabs/TradeAnalyticsTab";
import RiskExposureTab from "../Backtesting/tabs/RiskExposureTab";

export default function TradingSimulatorPage() {
  const [portfolio, setPortfolio] = useState({});
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [globParams, setGlobParams] = useState({});
  const [basicParams, setBasicParams] = useState({});
  const [advancedParams, setAdvancedParams] = useState({});

  const [activeTab, setActiveTab] = useState(null);

  const { benchmarkData } = useSymbols();

  
  const {
    availablePortfolios,
    getPortoliosLoading,
    getPortfoliosError
  } = useLoadPortfolios()

  const {
    backtestResult, 
    runBacktest, 
    isLoading: backtestLoading, 
    error: backtestError 
  } = useBacktest();

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
    if (portfolio && Object.keys(portfolio).length > 0) {
      console.log(portfolio.value.data)
      const stratParams = Object.fromEntries(
        Object.entries(portfolio.value.data).flatMap(([strat, stratResult]) => 
          Object.entries(stratResult.params).map(([param, paramValue]) => {
            console.log(strat, param, strategies[strat].params.find(p => p.name === param))
            const { default: value, name, ...rest } = strategies[strat].params.find(p => p.name === param)
            return [
              name, 
              { value: paramValue, ...rest }
            ]
          })
        )
      );

      const allParams = {...stratParams, ...globParams};
      const basic = Object.fromEntries(
        Object.entries(allParams).filter(([_, param]) => param.category === "basic")
      );
      const advanced = Object.fromEntries(
        Object.entries(allParams).filter(([_, param]) => param.category === "advanced")
      );
      console.log(basic, advanced, allParams)
      setBasicParams(basic);
      setAdvancedParams(advanced);
    }
  }, [portfolio, globParams])

  const handleRunBacktest = async () => {
    console.log(portfolio.value.data)
    const syms = Object.entries(portfolio.value.data).flatMap(([strat, stratResults]) => 
      stratResults.symbols.map(s => ({
        "symbols": s.symbol.split("-"),
        "strategy": strat,
        "weight": s.weight
      }))
    );

    setAdvancedParams((prev) => ({
      ...prev,
      [startDate]: { ...prev[startDate], value: startDate.value },
      [endDate]: { ...prev[endDate], value: endDate.value },
    }))
    console.log(advancedParams, basicParams, syms)
    await runBacktest({symbolItems: syms, basicParams, advancedParams})
  }
  

  return (
      <div className="space-y-6">
        {/* Strategy + Params */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SingleSelect
            currentValue={portfolio}
            setCurrentValue={setPortfolio}
            options={availablePortfolios}
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

          <button
            onClick={handleRunBacktest}
            disabled={
              backtestLoading || Object.keys(portfolio).length === 0
            }
            className={"px-4 py-2 rounded-lg text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"}
          >
            {backtestLoading ? "Running..." : "Run Backtest"}
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
              <OverviewTab results={backtestResult} benchmark={benchmarkData} />
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