import UniverseFilter from "./components/stages/Stage1UniverseFilter"
import PreScreen from "./components/stages/Stage2PreScreen"
import PreliminaryBacktest from "./components/stages/Stage3PreliminaryBacktest";
import StrategySelection from "./components/stages/Stage4StrategySelect";
import GAOptimisation from "./components/stages/Stage5GAOptimiser";

import { useState } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";
import { usePreScreen } from "./hooks/usePreScreen";
import { usePrelimBacktest } from "./hooks/usePrelimBacktest";
import { useStrategySelect } from "./hooks/useStrategySelect";

const precomputedPrelimBacktestResults = {
    "AAPL": ["breakout", "sma_crossover"],
    "MSFT": ["momentum", "rsi_reversion"],
    "AAPL-MSFT": ["pairs_trading"]
    // ...etc
  };

export default function PortfolioBuilder() {
  const [showUniFilter, setShowUniFilter] = useState(false);
  const [showPreScreen, setShowPreScreen] = useState(false);
  const [showPrelimBacktest, setShowPrelimBacktest] = useState(false);
  const [showStrategySelector, setShowStrategySelector] = useState(false);
  const [showGAOptimiser, setShowGAOptimiser] = useState(false);

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
    filterResults: strategySelectFilterResults,
    runStrategySelect,
    isLoading: strategySelectLoading,
    error: strategySelectError,
    strategyType: strategySelectStrategyType,
    uploadComplete: strategySelectUploadComplete,
    progress: strategySelectProgress
  } = useStrategySelect(backtestFilterResults, setShowStrategySelector)

  const handleUniverseFilters = async () => {
    await filterUniverse();
  };

  const handlePreScreen = async () => {
    await preScreen();
  }

  const handlePrelimBacktest = async () => {
    await runPrelimBacktest()
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
        onRunStrategySelect={runStrategySelect}
        visible={showStrategySelector}
        setVisible={setShowStrategySelector}
        filterResults={strategySelectFilterResults}
        strategySelectLoading={strategySelectLoading}
        strategySelectError={strategySelectError}
        prelimBacktestResults={backtestFilterResults}
        strategyType={strategySelectStrategyType}
        uploadComplete={strategySelectUploadComplete}
        progress={strategySelectProgress}
      />
      <GAOptimisation 
        visible={showGAOptimiser}
        setVisible={setShowGAOptimiser}
      />
    </div>
  );
}
