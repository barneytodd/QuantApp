import { useState, useEffect } from "react";
import { useSymbols } from "./hooks/useSymbols";
import { useStrategyParams } from "./hooks/useStrategyParams";
import { useBacktest } from "./hooks/useBacktest";
import { useOptimisation } from "./hooks/useOptimisation";
import { useOptimisationParams } from "./hooks/useOptimisationParams";
import { usePairs } from "./hooks/usePairs";

import StrategySelector from "./components/StrategySelector";
import SymbolSelector from "./components/SymbolSelector";
import ParamsCard from "./components/ParamsCard";
import PairsSelectionTable from "./components/PairsSelectionTable";
import AdvancedOptionsPanel from "./components/AdvancedOptionsPanel";
import OptimiserPanel from "./components/OptimiserPanel";
import CustomTextBox from "./components/CustomTextBox";

import OverviewTab from "./tabs/OverviewTab";
import TradeAnalyticsTab from "./tabs/TradeAnalyticsTab";
import RiskExposureTab from "./tabs/RiskExposureTab";

export default function Backtesting() {
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [showPairs, setShowPairs] = useState(false);
  const [showCustom, setShowCustom] = useState(false);

  const [activeTab, setActiveTab] = useState(null);

  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [isOptimiseOpen, setIsOptimiseOpen] = useState(false);
  const [customStrategy, setCustomStrategy] = useState(null);

  const { symbols, benchmarkData } = useSymbols();
  const { backtestResult, runBacktest, isLoading: backtestLoading, error: backtestError } = useBacktest();
  const { optimParams, setOptimParams } = useOptimisationParams()
  const { optimisationResult, optimiseParameters, isLoading: optimLoading, error: optimError } = useOptimisation();
  
  const { 
    pairCandidates, 
    selectedPairs, 
    setSelectedPairs, 
    selectPairs, 
    isLoading: pairsLoading, 
    error: pairsError 
  } = usePairs();

  const {
    strategyType,
    setStrategyType,
    strategyTypeOptions,
    basicParams,
    setBasicParams,
    advancedParams,
    setAdvancedParams
  } = useStrategyParams();

  

  // --- handlers ---
  const handleRunBacktest = async () => {
    const syms = strategyType?.value === "custom" 
      ? customStrategy.flatMap((s) =>
        s.symbols.map((symbol, idx) => ({
          symbols: [symbol],
          strategy: s.name,
          weight: s.weights[idx] ?? null, // use null if weight is missing
        })))
      : strategyType?.value === "pairs_trading" 
        ? selectedPairs.map(p => ({
            symbols: [p.stock1, p.stock2],
            strategy: strategyType?.value,
            weight: null
          }))
        : selectedSymbols.map(s => ({
            symbols: [s.value],
            strategy: strategyType?.value,
            weight: null
          }))
    await runBacktest({ symbolItems: syms, strategyType, basicParams, advancedParams, selectedPairs });
  };

  useEffect(() => {
    if (!backtestError && backtestResult) {
      setActiveTab("Overview");
    }
  }, [backtestError, backtestResult]);


  const handleOptimise = async () => {
    await optimiseParameters({ symbols: selectedSymbols, strategyType, basicParams, advancedParams, optimParams, selectedPairs });
    if (!optimisationResult || optimError !== null) {
      return;
    }

    if (!optimisationResult.best_basic_params) {
      return;
    }
    else {
      const basic = optimisationResult.best_basic_params;
      setBasicParams(prev => {
        const updated = { ...prev };
        for (const k in basic) {
          updated[k] = { ...(prev[k] || {}), value: basic[k] };
        }
        return updated;
      });
    }

    if (!optimisationResult.best_advanced_params) {
      return;
    }
    else {
      const advanced = optimisationResult.best_advanced_params;
      setAdvancedParams(prev => {
        const updated = { ...prev };
        for (const k in advanced) {
          updated[k] = { ...(prev[k] || {}), value: advanced[k] };
        }
        return updated;
      });
    }

  };


  const handleSelectPairs = async () => {
    await selectPairs(selectedSymbols.map((s) => s.value));
    setShowPairs(true);
  };


  useEffect(() => {
    if (strategyType !== "custom") {
      setShowCustom(false);
    }
    if (strategyType !== "pairs_trading") {
      setShowPairs(false)
    }
  }, [strategyType]);


  return (
    <div className="space-y-6">
      {/* Strategy + Params */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StrategySelector
          strategyType={strategyType}
          setStrategyType={setStrategyType}
          options={strategyTypeOptions}
        />

        <SymbolSelector
          symbols={symbols}
          selectedSymbols={selectedSymbols}
          setSelectedSymbols={setSelectedSymbols}
        />

        <CustomTextBox
          strategyType={strategyType}
          customStrategy={customStrategy}
          setCustomStrategy={setCustomStrategy}
          strategyOptions={strategyTypeOptions}
          visible={showCustom}
          setVisible={setShowCustom}
        />

        <ParamsCard
          basicParams={basicParams}
          setBasicParams={setBasicParams}

          selectedSymbols={selectedSymbols}
          strategyType={strategyType}

          onSelectPairs={handleSelectPairs}
          pairsLoading={pairsLoading}
          pairsError={pairsError}
          selectedPairs={selectedPairs}

          onOpenAdvanced={() => setIsAdvancedOpen(true)}
          
          onOpenOptimiser={() => setIsOptimiseOpen(true)}
          optimLoading={optimLoading}
          optimError={optimError}

          onRunBacktest={handleRunBacktest}
          backtestLoading={backtestLoading}
        />
      </div>

      {/* Pairs table */}
      <PairsSelectionTable
        strategyType={strategyType}
        pairCandidates={pairCandidates}
        selectedPairs={selectedPairs}
        setSelectedPairs={setSelectedPairs}
        visible={showPairs}
        setVisible={setShowPairs}
      />

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

      {/* Side Panels */}
      <AdvancedOptionsPanel
        isOpen={isAdvancedOpen}
        onClose={() => setIsAdvancedOpen(false)}
        advancedParams={advancedParams}
        setAdvancedParams={setAdvancedParams}
      />

      <OptimiserPanel
        isOpen={isOptimiseOpen}
        onClose={() => setIsOptimiseOpen(false)}
        optimisationParams={optimParams}
        setOptimisationParams={setOptimParams}
        onRunOptimisation={handleOptimise}
        optimLoading={optimLoading}
      />
    </div>
  );
}
