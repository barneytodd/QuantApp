import { useState, useEffect, useMemo } from "react";
import { strategies } from "../strategies/strategyRegistry";
import { globalParams } from "../strategies/globalParams";

export function useStrategyParams() {
  const [strategyType, setStrategyType] = useState(null);
  const [basicParams, setBasicParams] = useState({});
  const [advancedParams, setAdvancedParams] = useState({});

  const strategyTypeOptions = useMemo(
    () =>
      Object.entries(strategies).map(([key, strat]) => ({
        value: key,
        label: strat.label,
      })),
    []
  );

  // default strategy
  useEffect(() => {
    if (!strategyType && strategyTypeOptions.length > 0) {
      setStrategyType(strategyTypeOptions[0]);
    }
  }, [strategyTypeOptions, strategyType]);

  // default params for strategy
  useEffect(() => {
    if (strategyType) {
      const allParams = [
        ...globalParams,
        ...(strategyType.value === "custom"
          ? Object.values(strategies)
              .filter(s => s.value !== "custom") 
              .flatMap(s => s.params)           
          : strategies[strategyType.value].params
        ),
      ];

      const basic = allParams.filter((p) => p.category === "basic");
      const advanced = allParams.filter((p) => p.category === "advanced");

      const basicDefaults = Object.fromEntries(
        basic.map((p) => [
          p.name,
          { value: p.default, label: p.label, type: p.type, bounds: p.bounds, optimise: p.optimise, integer: p.integer, category: p.category, options: p.options },
        ])
      );
      const advancedDefaults = Object.fromEntries(
        advanced.map((p) => [
          p.name,
          { value: p.default, label: p.label, type: p.type, bounds: p.bounds, optimise: p.optimise, integer: p.integer, category: p.category, options: p.options },
        ])
      );

      setBasicParams(basicDefaults);
      setAdvancedParams(advancedDefaults);
    }

  }, [strategyType]);
  return {
    strategyType,
    setStrategyType,
    strategyTypeOptions,
    basicParams,
    setBasicParams,
    advancedParams,
    setAdvancedParams,
  };
}
