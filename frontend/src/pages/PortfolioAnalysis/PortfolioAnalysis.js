import UniverseFilter from "./components/stages/Stage1UniverseFilter"
import PreScreen from "./components/stages/Stage2PreScreen"
import PreliminaryBacktest from "./components/stages/Stage3PreliminaryBacktest";
import StrategySelection from "./components/stages/Stage4StrategySelect";
import ParamOptimisation from "./components/stages/Stage5ParamOptimsation";
import PortfolioWeights from "./components/stages/Stage6PortfolioWeights";
import ParamCard from "../../components/ui/ParamCard";

import { useEffect, useState } from "react"
import { useUniverseFilters } from "./hooks/useUniverseFilters";
import { usePreScreen } from "./hooks/usePreScreen";
import { usePrelimBacktest } from "./hooks/usePrelimBacktest";
import { useStrategySelect } from "./hooks/useStrategySelect";
import { useParamOptimisation } from "./hooks/useParamOptimisation"
import { usePortfolioWeights } from "./hooks/usePortfolioWeights";


export default function PortfolioBuilder() {
  const [showUniFilter, setShowUniFilter] = useState(false);
  const [showPreScreen, setShowPreScreen] = useState(false);
  const [showPrelimBacktest, setShowPrelimBacktest] = useState(false);
  const [showStrategySelector, setShowStrategySelector] = useState(false);
  const [showParamOptimisation, setShowParamOptimisation] = useState(false);
  const [showPortfolioWeights, setShowPortfolioWeights] = useState(false);

  const [startDate, setStartDate] = useState({});
  const [endDate, setEndDate] = useState({});

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
  } = usePreScreen(uniFilterResults, endDate, setShowPreScreen);

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
  } = usePrelimBacktest(preScreenFilterResults, startDate, endDate, setShowPrelimBacktest);

  const {
    paramValues: strategySelectParamValues,
    setParamValues: setStrategySelectParamValues,
    filterResults: strategySelectResults,
    metricRanges: strategySelectMetricRanges,
    runStrategySelect,
    isLoading: strategySelectLoading,
    error: strategySelectError,
    strategyType: strategySelectStrategyType,
    uploadComplete: strategySelectUploadComplete,
    progress: strategySelectProgress,
    portfolio: strategySelectPortfolio
  } = useStrategySelect(backtestFilterResults, startDate, endDate, setShowStrategySelector)

  const {
    optimisationParams: paramOptimisationParams,
    setOptimisationParams: setParamOptimisationParams,
    optimisationResult: paramOptimisationResults,
    runParamOptimisation,
    optimLoading: paramOptimisationLoading,
    optimError: paramOptimisationError,
    progress: paramOptimisationProgress,
    portfolio: paramOptimisationPortfolio
  } = useParamOptimisation(strategySelectResults, strategySelectMetricRanges, startDate, endDate, setShowParamOptimisation)

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
  } = usePortfolioWeights(paramOptimisationResults, setShowPortfolioWeights)

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

  const handleSavePortfolioToDB = async (result) => {
    await savePortfolioToDB(result);
  }

  useEffect(() => {
    const today = new Date();
    const start = new Date();
    const end = new Date()
    start.setFullYear(today.getFullYear() - 11);
    end.setFullYear(today.getFullYear() - 1)

    const startStr = start.toISOString().split("T")[0].replace(/-/g, "-");
    const endStr = end.toISOString().split("T")[0].replace(/-/g, "-");

    setStartDate({value: startStr, type: "date", label: "Start Date"})
    setEndDate({value: endStr, type: "date", label: "End Date"})
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Build Portfolio</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ParamCard
          param={startDate} 
          setParam={setStartDate}
        />
        <ParamCard
          param={endDate}
          setParam={setEndDate}
        />
      </div>
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
        onSavePortfolio={handleSavePortfolioToDB}
        savingPortfolio={savingPortfolio}
        savedPortfolio={savedPortfolio}
        portfolio={strategySelectPortfolio}
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
        onSavePortfolio={handleSavePortfolioToDB}
        savingPortfolio={savingPortfolio}
        savedPortfolio={savedPortfolio}
        portfolio={paramOptimisationPortfolio}
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
        paramOptimisationResults={paramOptimisationResults}
        onSavePortfolio={handleSavePortfolioToDB}
        savingPortfolio={savingPortfolio}
        savedPortfolio={savedPortfolio}
      />
    </div>
  );
}
