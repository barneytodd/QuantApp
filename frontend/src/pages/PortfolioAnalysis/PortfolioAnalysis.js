import UniverseFilter from "./components/filters/Stage1UniverseFilter"
import PreScreen from "./components/filters/Stage2PreScreen"
import InitialBacktest from "./components/filters/Stage3ShortBacktest";
import StrategySelection from "./components/filters/Stage4StrategySelect";
import GAOptimisation from "./components/filters/Stage5GAOptimiser";

import { useState } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";
import { usePreScreen } from "./hooks/usePreScreen";

export default function PortfolioBuilder() {
  const [showUniFilter, setShowUniFilter] = useState(false);
  const [showPreScreen, setShowPreScreen] = useState(false);
  const [showBacktestFilter, setShowBacktestFilter] = useState(false);
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
    testingComplete: preScreenTestingComplete
  } = usePreScreen();

  const handleUniverseFilters = async () => {
    await filterUniverse();
  };

  const handlePreScreen = async () => {
    await preScreen(uniFilterResults);
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
      />
      <InitialBacktest
        visible={showBacktestFilter}
        setVisible={setShowBacktestFilter}
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
