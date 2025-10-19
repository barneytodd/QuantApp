import UniverseFilter from "./components/stages/Stage1UniverseFilter"
import PreScreen from "./components/stages/Stage2PreScreen"
import PreliminaryBacktest from "./components/stages/Stage3PreliminaryBacktest";
import StrategySelection from "./components/stages/Stage4StrategySelect";
import ParamOptimisation from "./components/stages/Stage5ParamOptimsation";
import PortfolioWeights from "./components/stages/Stage6PortfolioWeights";

import { useState } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";
import { usePreScreen } from "./hooks/usePreScreen";
import { usePrelimBacktest } from "./hooks/usePrelimBacktest";
import { useStrategySelect } from "./hooks/useStrategySelect";
import { useParamOptimisation } from "./hooks/useParamOptimisation"
import { usePortfolioWeights } from "./hooks/usePortfolioWeights";


const precomputedParamOptimisationResults = {
  "breakout": {
    "best_params": {"lookback": 20, "breakoutMultiplier": 0.0}, 
    "aggregated_results": [
      {"symbol": "AAPL", "strategy": "breakout", "returns": [
        0.0015, -0.0005, 0.0025, 0.001, -0.0015, 0.003, 0.002, -0.0005, 0.0015, 0.0005,
        -0.002, 0.001, 0.0005, -0.0005, 0.0015, 0.002, -0.001, 0.003, 0.0015, -0.0005,
        0.0005, 0.001, -0.001, 0.002, 0.0005, 0.001, -0.0005, 0.0025, 0.002, -0.001
      ]}
    ]
  },
  "sma_crossover": {
    "best_params": {"shortPeriod": 20, "longPeriod": 50},
    "aggregated_results": [
      {"symbol": "MSFT", "strategy": "sma_crossover", "returns": [
        0.002, -0.001, 0.003, 0.001, -0.002, 0.004, 0.003, -0.001, 0.002, 0.001,
        -0.003, 0.002, 0.001, -0.001, 0.002, 0.003, -0.002, 0.004, 0.002, -0.001,
        0.001, 0.002, -0.002, 0.003, 0.001, 0.002, -0.001, 0.004, 0.003, -0.002
      ]}
    ]
  },
  "pairs_trading": {
    "best_params": {"lookback": 20, "entryZ": 2, "exitZ": 0.5, "hedgeRatio": 1.0},
    "aggregated_results": [
      {"symbol": "AMZN-GOOG", "strategy": "pairs_trading", "returns": [
        0.004, -0.003, 0.006, 0.002, -0.004, 0.008, 0.005, -0.002, 0.004, 0.003,
        -0.006, 0.004, 0.002, -0.003, 0.004, 0.006, -0.004, 0.007, 0.004, -0.002,
        0.002, 0.003, -0.003, 0.005, 0.002, 0.003, -0.002, 0.006, 0.005, -0.003
      ]}
    ]
  }
}

export default function PortfolioBuilder() {
  const [showUniFilter, setShowUniFilter] = useState(false);
  const [showPreScreen, setShowPreScreen] = useState(false);
  const [showPrelimBacktest, setShowPrelimBacktest] = useState(false);
  const [showStrategySelector, setShowStrategySelector] = useState(false);
  const [showParamOptimisation, setShowParamOptimisation] = useState(false);
  const [showPortfolioWeights, setShowPortfolioWeights] = useState(false);

  const {
    filterValues: uniFilterValues, 
    setFilterValues: setUniFilterValues, 
    filterResults: uniFilterResults, 
    filterUniverse,
    isLoading: uniLoading,
    error: uniError
  } = useUniverseFilters();

  const {
    filterValues: preScreenFilterValues, 
    setFilterValues: setPreScreenFilterValues, 
    filterResults: preScreenFilterResults, 
    preScreen,
    isLoading: preScreenLoading,
    error: preScreenError,
    uploadComplete: preScreenUploadComplete,
    testingComplete: preScreenTestingComplete,
    progress: preScreenTestingProgress,
    fails: preScreenFails
  } = usePreScreen(uniFilterResults, setShowPreScreen);

  const {
    filterValues: backtestFilterValues,
    setFilterValues: setBacktestFilterValues,
    filterResults: backtestFilterResults,
    runPrelimBacktest,
    isLoading: backtestLoading,
    error: backtestError,
    strategyType: backtestStrategyType,
    pairsLoading: BacktestPairsLoading,
    pairsProgress: BacktestPairsProgress
  } = usePrelimBacktest(preScreenFilterResults, setShowPrelimBacktest);

  const {
    paramValues: strategySelectParamValues,
    setParamValues: setStrategySelectParamValues,
    filterResults: strategySelectResults,
    runStrategySelect,
    isLoading: strategySelectLoading,
    error: strategySelectError,
    strategyType: strategySelectStrategyType,
    uploadComplete: strategySelectUploadComplete,
    progress: strategySelectProgress
  } = useStrategySelect(backtestFilterResults, setShowStrategySelector)

  const {
    optimisationParams: paramOptimisationParams,
    setOptimisationParams: setParamOptimisationParams,
    optimisationResult: paramOptimisationResults,
    runParamOptimisation,
    optimLoading: paramOptimisationLoading,
    optimError: paramOptimisationError,
    progress: paramOptimisationProgress
  } = useParamOptimisation(strategySelectResults, setShowParamOptimisation)

  const {
    portfolioWeightsParams,
    setPortfolioWeightsParams,
    portfolioWeightsResult,
    runPortfolioWeights,
    isLoading: portfolioWeightsLoading,
    loadingInputs: portfolioWeightsInputsLoading,
    loadingHrp: portfolioWeightsHrpLoading,
    loadingOptimisation: portfolioWeightsOptimisationLoading,
    error: portfolioWeightsError,
    savePortfolioToDB,
    saving: savingPortfolio,
    saved: savedPortfolio
  } = usePortfolioWeights(precomputedParamOptimisationResults, setShowPortfolioWeights)

  const handleUniverseFilters = async () => {
    await filterUniverse();
  };

  const handlePreScreen = async () => {
    await preScreen();
  }

  const handlePrelimBacktest = async () => {
    await runPrelimBacktest();
  }

  const handleStrategySelect = async () => {
    await runStrategySelect();
  }

  const handleParamOptimisation = async () => {
    await runParamOptimisation();
  }

  const handlePortfolioWeights = async () => {
    await runPortfolioWeights();
  }

  const handleSavePortfolioToDB = async () => {
    await savePortfolioToDB(portfolioWeightsResult);
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Build Portfolio</h1>
      <UniverseFilter 
        filterValues={uniFilterValues}
        setFilterValues={setUniFilterValues}
        onFilterUniverse={handleUniverseFilters}
        visible={showUniFilter}
        setVisible={setShowUniFilter}
        filterResults={uniFilterResults}
        uniLoading={uniLoading}
        uniError={uniError}
      />
      <PreScreen
        filterValues={preScreenFilterValues}
        setFilterValues={setPreScreenFilterValues}
        onPreScreen={handlePreScreen}
        visible={showPreScreen}
        setVisible={setShowPreScreen}
        filterResults={preScreenFilterResults}
        preScreenLoading={preScreenLoading}
        preScreenError={preScreenError}
        uploadComplete={preScreenUploadComplete}
        testingComplete={preScreenTestingComplete}
        uniFilterResults={uniFilterResults}
        progress={preScreenTestingProgress}
        fails={preScreenFails}
      />
      <PreliminaryBacktest
        filterValues={backtestFilterValues}
        setFilterValues={setBacktestFilterValues}
        onRunBacktest={handlePrelimBacktest}
        visible={showPrelimBacktest}
        setVisible={setShowPrelimBacktest}
        filterResults={backtestFilterResults}
        backtestLoading={backtestLoading}
        backtestError={backtestError}
        preScreenResults={preScreenFilterResults}
        strategyType={backtestStrategyType}
        pairsLoading={BacktestPairsLoading}
        pairsProgress={BacktestPairsProgress}
      />
      <StrategySelection 
        paramValues={strategySelectParamValues}
        setParamValues={setStrategySelectParamValues}
        onRunStrategySelect={handleStrategySelect}
        visible={showStrategySelector}
        setVisible={setShowStrategySelector}
        filterResults={strategySelectResults}
        strategySelectLoading={strategySelectLoading}
        strategySelectError={strategySelectError}
        prelimBacktestResults={backtestFilterResults}
        strategyType={strategySelectStrategyType}
        uploadComplete={strategySelectUploadComplete}
        progress={strategySelectProgress}
      />
      <ParamOptimisation 
        onRunParamOptimisation={handleParamOptimisation}
        visible={showParamOptimisation}
        setVisible={setShowParamOptimisation}
        paramValues={paramOptimisationParams}
        setParamValues={setParamOptimisationParams}
        filterResults={paramOptimisationResults}
        paramOptimisationLoading={paramOptimisationLoading}
        paramOptimisationError={paramOptimisationError}
        strategySelectResults={strategySelectResults}
        progress={paramOptimisationProgress}
      />
      <PortfolioWeights 
        onRunPortfolioWeights={handlePortfolioWeights}
        visible={showPortfolioWeights}
        setVisible={setShowPortfolioWeights}
        paramValues={portfolioWeightsParams}
        setParamValues={setPortfolioWeightsParams}
        filterResults={portfolioWeightsResult}
        portfolioWeightsLoading={portfolioWeightsLoading}
        inputsLoading={portfolioWeightsInputsLoading}
        hrpLoading={portfolioWeightsHrpLoading}
        optimisationLoading={portfolioWeightsOptimisationLoading}
        portfolioWeightsError={portfolioWeightsError}
        paramOptimisationResults={precomputedParamOptimisationResults}
        onSavePortfolio={handleSavePortfolioToDB}
        savingPortfolio={savingPortfolio}
        savedPortfolio={savedPortfolio}
      />
    </div>
  );
}
