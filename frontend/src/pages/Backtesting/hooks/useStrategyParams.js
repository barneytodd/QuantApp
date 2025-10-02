import { useState, useEffect, useMemo } from "react";
import { strategies } from "../strategies/strategyRegistry";
import { globalParams } from "../strategies/globalParams";

export function useStrategyParams(selectedSymbols, selectedPairs) {
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
          { 
            value: p.default, 
            label: p.label, 
            type: p.type, 
            bounds: p.bounds, 
            optimise: p.optimise, 
            integer: p.integer, 
            category: p.category, 
            options: p.options, 
            info: p.info,
            group: p.group,
            lookback: p.lookback
          },
        ])
      );
      const advancedDefaults = Object.fromEntries(
        advanced.map((p) => [
          p.name,
          { 
            value: p.default, 
            label: p.label, 
            type: p.type, 
            bounds: p.bounds, 
            optimise: p.optimise, 
            integer: p.integer, 
            category: p.category, 
            options: p.options,
            info: p.info,
            group: p.group,
            lookback: p.lookback
          },
        ])
      );

      setBasicParams(basicDefaults);
      setAdvancedParams(advancedDefaults);
    }

  }, [strategyType]);

  // add weight to advanced params for each selected stock
  useEffect(() => {
    setAdvancedParams((prev) => {
      const newParams = { ...prev };

      const symbols = strategyType?.value === "pairs_trading" 
        ? selectedPairs?.flatMap(obj => `${obj.stock1}-${obj.stock2}`)
        : selectedSymbols?.flatMap(obj => obj.label)
      
      symbols.forEach((symbol) => {
        const key = `${symbol}_weight`;
        newParams[key] = {
          name: key,
          label: `${symbol} Weight`,
          value: 1/symbols.length,
          type: "number",
          optimise: false,
          group: "Capital Allocation",
          info: `Allocation of initial capital towards ${symbol} \nRequired: value, total weight ε [0,1]`,
        };
      });

      // Remove weights for stocks that are no longer selected
      Object.keys(newParams).forEach((key) => {
        if (key.endsWith("_weight") && !symbols.includes(key.replace("_weight", ""))) {
          delete newParams[key];
        }
      });

      return newParams;
    });
  }, [selectedSymbols, selectedPairs, strategyType?.value]);

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
