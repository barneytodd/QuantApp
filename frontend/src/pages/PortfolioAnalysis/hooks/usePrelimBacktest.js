import { useState, useEffect } from "react";
import { filters } from "../filters/prelimBacktestFilters"
import { strategies } from "../../Backtesting/parameters/strategyRegistry";
import { useStrategyParams } from "../../Backtesting/hooks/useStrategyParams";

export function usePrelimBacktest() {
    const [filterValues, setFilterValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // default filters
    useEffect(() => {
        const filterDefaults = Object.fromEntries(
            Object.values(filters).map((f) => {
                const { default: value, name, ...rest } = f;
                return [name, { value, ...rest }];
            })
        );
        setFilterValues(filterDefaults);
        console.log(filterDefaults)
    }, [])

    const basicParams = {}
    const advancedParams = {}

    const runBacktest = async (preScreenResults) => {
        if (!preScreenResults) return;
        try {
            const symbolItems = Object.entries(preScreenResults).flatMap(
                ([symbol, types]) =>
                    // for each type, find all strategies that match that type
                    types.flatMap(type =>
                        Object.entries(strategies)
                            .filter(([strategyName, strategyObj]) => strategyObj.type === type)
                            .map(([strategyName, strategyObj]) => ({
                                symbol,
                                strategy: strategyName,
                                params: strategyObj.params
                            }))
                    )
                );

            const params = Object.fromEntries(
            Object.entries(advancedParams)
                .filter(([key, _]) => !key.endsWith("_weight"))
                .map(([k, v]) => [k, { value: v.value, lookback: v.lookback ?? false }])
                .concat(
                Object.entries(basicParams).map(([k, v]) => [k, { value: v.value, lookback: v.lookback ?? false }])
                )
            )

            const res = await fetch("http://localhost:8000/api/strategies/backtest", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({symbolItems: symbolItems, params: params}),
            });

            if (!res.ok) {
                alert("Backtest failed");
                return; 
            }
            const data = await res.json();
            setFilterResults(data);
            return data;
        } catch (err) {
            setError(err);
            alert("Backtest failed");
        } finally {
            setIsLoading(false);
        }
    }

    return {
        filterValues,
        setFilterValues,
        filterResults,
        runBacktest,
        isLoading,
        error
    }
}