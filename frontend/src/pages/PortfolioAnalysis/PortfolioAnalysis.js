import UniverseFilter from "./components/stages/Stage1UniverseFilter"
import PreScreen from "./components/stages/Stage2PreScreen"
import PreliminaryBacktest from "./components/stages/Stage3PreliminaryBacktest";
import StrategySelection from "./components/stages/Stage4StrategySelect";
import ParamOptimisation from "./components/stages/Stage5ParamOptimsation";

import { useState } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";
import { usePreScreen } from "./hooks/usePreScreen";
import { usePrelimBacktest } from "./hooks/usePrelimBacktest";
import { useStrategySelect } from "./hooks/useStrategySelect";
import { useParamOptimisation } from "./hooks/useParamOptimisation"

const precomputedStrategySelectResults = {
    "AAPL": {strategy: "breakout", score: 1},
    "MSFT": {strategy: "momentum", score: 0.5},
    "AMZN-GOOG": {strategy: "pairs_trading", score: 0.75}
    // ...etc
  };

export default function PortfolioBuilder() {
  const [showUniFilter, setShowUniFilter] = useState(false);
  const [showPreScreen, setShowPreScreen] = useState(false);
  const [showPrelimBacktest, setShowPrelimBacktest] = useState(false);
  const [showStrategySelector, setShowStrategySelector] = useState(false);
  const [showParamOptimisation, setShowParamOptimisation] = useState(false);

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
    paramValues: paramOptimisationParamValues,
    setParamValues: setParamOptimisationParamValues,
    filterResults: paramOptimisationResults,
    runParamOptimisation,
    isLoading: paramOptimisationLoading,
    error: paramOptimisationError,
    strategyType: paramOptimisationStrategyType,
    uploadComplete: paramOptimisationUploadComplete,
    progress: paramOptimisationProgress
  } = useParamOptimisation(precomputedStrategySelectResults, setShowParamOptimisation)

  const handleUniverseFilters = async () => {
    await filterUniverse();
  };

  const handlePreScreen = async () => {
    await preScreen();
  }

  const handlePrelimBacktest = async () => {
    await runPrelimBacktest()
  }

  const handleStrategySelect = async () => {
    await runStrategySelect()
  }

  const handleParamOptimisation = async () => {
    await runParamOptimisation()
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
        paramValues={paramOptimisationParamValues}
        setParamValues={setParamOptimisationParamValues}
        onRunParamOptimisation={handleParamOptimisation}
        visible={showParamOptimisation}
        setVisible={setShowParamOptimisation}
        filterResults={paramOptimisationResults}
        paramOptimisationLoading={paramOptimisationLoading}
        paramOptimisationError={paramOptimisationError}
        strategySelectResults={precomputedStrategySelectResults}
        strategyType={paramOptimisationStrategyType}
        uploadComplete={paramOptimisationUploadComplete}
        progress={paramOptimisationProgress}
      />
    </div>
  );
}
