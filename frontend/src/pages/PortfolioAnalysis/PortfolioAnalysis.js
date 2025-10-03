import UniverseFilter from "./components/filters/Stage1UniverseFilter"
import InitialBacktest from "./components/filters/Stage2ShortBacktest";
import StrategySelection from "./components/filters/Stage3StrategySelect";
import GAOptimisation from "./components/filters/Stage4GAOptimiser";

import { useState, useEffect } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";

export default function PortfolioBuilder() {
  const [showUniFilter, setShowUniFilter] = useState(false);
  const [showBacktestFilter, setShowBacktestFilter] = useState(false);
  const [showStrategySelector, setShowStrategySelector] = useState(false);
  const [showGAOptimiser, setShowGAOptimiser] = useState(false);

  const {
    filterValues, 
    setFilterValues, 
    filterResults, 
    filterUniverse,
    isLoading: uniLoading,
    error: uniError
  } = useUniverseFilters();

  const handleUniverseFilters = async () => {
    await filterUniverse();
  };

  useEffect(() => {
    console.log(filterResults)
  }, [filterResults])


  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Build Portfolio</h1>
      <UniverseFilter 
        filterValues={filterValues}
        setFilterValues={setFilterValues}
        onFilterUniverse={handleUniverseFilters}
        visible={showUniFilter}
        setVisible={setShowUniFilter}
        filterResults={filterResults}
        uniLoading={uniLoading}
        uniError={uniError}
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
