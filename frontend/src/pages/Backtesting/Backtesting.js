import { useState } from "react";
import { useSymbols } from "./hooks/useSymbols";
import { useStrategyParams } from "./hooks/useStrategyParams";
import { useBacktest } from "./hooks/useBacktest";
import { useOptimisation } from "./hooks/useOptimisation";
import { usePairs } from "./hooks/usePairs";

import StrategySelector from "./components/StrategySelector";
import SymbolSelector from "./components/SymbolSelector";
import ParamsCard from "./components/ParamsCard";
import PairsSelectionTable from "./components/PairsSelectionTable";
import AdvancedOptionsPanel from "./components/AdvancedOptionsPanel";
import OptimiserPanel from "./components/OptimiserPanel";

import OverviewTab from "./tabs/OverviewTab";
import TradeAnalyticsTab from "./tabs/TradeAnalyticsTab";
import RiskExposureTab from "./tabs/RiskExposureTab";

export default function Backtesting() {
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [showPairs, setShowPairs] = useState(false);

  const [activeTab, setActiveTab] = useState(null);

  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [isOptimiseOpen, setIsOptimiseOpen] = useState(false);

  const { symbols, benchmarkData } = useSymbols();
  const { backtestResult, runBacktest, isLoading: backtestLoading } = useBacktest();
  const { optimisationResult, optimiseParameters } = useOptimisation();
  
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
    setAdvancedParams,
  } = useStrategyParams();

  // --- handlers ---
  const handleRunBacktest = async () => {
    await runBacktest({ symbols: selectedSymbols, strategyType, basicParams, advancedParams, selectedPairs });
    setActiveTab("Overview");
  };

  const handleOptimise = async () => {
    await optimiseParameters({ symbols: selectedSymbols, strategyType, basicParams, advancedParams });
  };

  const handleSelectPairs = async () => {
    await selectPairs(selectedSymbols.map((s) => s.value));
    setShowPairs(true);
  };

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

        <ParamsCard
          basicParams={basicParams}
          setBasicParams={setBasicParams}
          strategyType={strategyType}
          onSelectPairs={handleSelectPairs}
          pairsLoading={pairsLoading}
          pairsError={pairsError}
          onOpenAdvanced={() => setIsAdvancedOpen(true)}
          onOpenOptimiser={() => setIsOptimiseOpen(true)}
          onRunBacktest={handleRunBacktest}
          backtestLoading={backtestLoading}
        />
      </div>

      {/* Pairs table */}
      <PairsSelectionTable
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
            <OverviewTab backtestResult={backtestResult} benchmarkData={benchmarkData} />
          )}
          {activeTab === "Trade Analytics" && (
            <TradeAnalyticsTab backtestResult={backtestResult} />
          )}
          {activeTab === "Risk & Exposure" && (
            <RiskExposureTab backtestResult={backtestResult} />
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
        onRunOptimisation={handleOptimise}
      />
    </div>
  );
}
