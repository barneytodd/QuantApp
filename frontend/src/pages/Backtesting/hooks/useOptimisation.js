import { useState, useEffect } from "react";
import { strategies } from "../parameters/strategyRegistry";
import { globalParams } from "../parameters/globalParams";

export function useOptimisation(startDate=null, endDate=null) {
  const [optimisationResult, setOptimisationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stratParams, setStratParams] = useState({});
  const [globParams, setGlobParams] = useState({})

  useEffect(() => {
    const strategyParamsDict = Object.fromEntries(
      Object.entries(strategies).map(([strat, stratInfo]) => [
        strat,
        Object.fromEntries(
          stratInfo.params.map(p => [
            p.name,
            p.type === "number"
            ? {
                type: p.integer ? "int" : "float",
                min: p.bounds[0],
                max: p.bounds[1],
                lookback: p.lookback,
                value: p.default
              }
            : {
                type: p.type,
                choices: p.options,
                lookback: p.lookback,
                value: p.default
              }
          ])
        )
      ])
    );

    const today = new Date();
    const start = new Date();
    start.setFullYear(today.getFullYear() - 10);

    const startStr = start.toISOString().split("T")[0].replace(/-/g, "-");

    const globalParamsDict = Object.fromEntries(
      globalParams.map(g => ([
        g.name, 
        {
          value: g.name === "startDate" 
            ? startDate?.value ?? startStr
            : g.name === "endDate" 
              ? endDate?.value ?? g.default
              : g.default, 
          lookback: g.lookback ?? null
        }
      ]))
    )
    
    setStratParams(strategyParamsDict);
    setGlobParams(globalParamsDict);
  }, [endDate?.value, startDate?.value])
  

  const optimiseParameters = async ({ strategyTypesWithSymbols, optimParams, scoringParams }) => {
    setIsLoading(true);
    setError(null);
    setOptimisationResult(null);
    console.log(strategyTypesWithSymbols, optimParams)

    const strats = Object.fromEntries(
      Object.entries(strategyTypesWithSymbols).map(([strat, symbolItems]) => [
        strat,
        {
          symbolItems: symbolItems,
          param_space: stratParams[strat]
        }
      ])
    )

    const optimisationParams = Object.fromEntries(
      Object.entries(optimParams).map(([name, param]) => [
        name,
        param.value
      ])
    )

    const payload = {
      strategies: strats,
      globalParams: globParams,
      optimParams: optimisationParams,
      scoringParams: scoringParams
    };

    console.log(payload)

    try {
      const res = await fetch("http://localhost:8000/api/params/optimise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Optimisation failed");
        return;
      }

      const data = await res.json();
      setOptimisationResult(data);
      return data;
    } catch (err) {
      setError(err);
      setIsLoading(false);
      alert("Optimisation failed");
    } finally {
      setIsLoading(false);
    }
  };

  return { optimisationResult, setOptimisationResult, optimiseParameters, isLoading, error };
}
