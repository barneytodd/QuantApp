import UniverseFilter from "./components/filters/Stage1UniverseFilter"
import PreScreen from "./components/filters/Stage2PreScreen"
import PreliminaryBacktest from "./components/filters/Stage3PreliminaryBacktest";
import StrategySelection from "./components/filters/Stage4StrategySelect";
import GAOptimisation from "./components/filters/Stage5GAOptimiser";

import { useState } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";
import { usePreScreen } from "./hooks/usePreScreen";
import { usePrelimBacktest } from "./hooks/usePrelimBacktest"

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
  } = usePreScreen();

  const {
    filterValues: backtestFilterValues,
    setFilterValues: setBacktestFilterValues,
    filterResults: backtestFilterResults,
    runBacktest,
    isLoading: backtestLoading,
    error: backtestError
  } = usePrelimBacktest();

  const handleUniverseFilters = async () => {
    await filterUniverse();
  };

  const handlePreScreen = async () => {
    await preScreen(uniFilterResults);
  }

  const handlePrelimBacktest = async () => {
    await runBacktest()
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
      />
      <StrategySelection 
        visible={showStrategySelector}
        setVisible={setShowStrategySelector}
      />
      <GAOptimisation 
        visible={showGAOptimiser}
        setVisible={setShowGAOptimiser}
      />
    </div>
  );
}
