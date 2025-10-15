import { useState, useEffect, useMemo } from "react";
import { params } from "../params/paramOptimisationParams"
import { useStrategyParams } from "../../Backtesting/hooks/useStrategyParams";

export function useParamOptimisation(strategySelectResults, setVisible) {
    const [paramValues, setParamValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [uploadComplete, setUploadComplete] = useState(true);
    const [progress, setProgress] = useState({});

    const allSymbols = useMemo(
        () => [
            ...new Set(
            Object.keys(strategySelectResults ?? {}).flatMap((s) => s.split("-"))
            )
        ],
        [strategySelectResults]
    )

    const selectedPairs = useMemo(
        () => Object.keys(strategySelectResults ?? {})
                .filter((s) => s.includes("-"))
                .map((s) => ({
                    "stock1": s.split("-")[0],
                    "stock2": s.split("-")[1]
                })), 
        [strategySelectResults]
    )

    const {
        strategyType,
        setStrategyType,
        basicParams,
        advancedParams,
    } = useStrategyParams(allSymbols, selectedPairs);

    // set default params
    useEffect(() => {
        const paramDefaults = Object.fromEntries(
            Object.values(params).map((p) => {
                const { default: value, name, ...rest } = p;
                return [name, { value, ...rest }];
            })
        );
        setParamValues(paramDefaults);
    }, [])

    useEffect(() => {
        setFilterResults(null);
        setVisible(false);
        setProgress({});
    }, [strategySelectResults, setVisible])

    useEffect(() => {
        if (allSymbols.length > 0 && strategyType?.value !== "custom") {
            setStrategyType({value: "custom", label: "custom"});
        }
    }, [allSymbols, selectedPairs, strategyType, setStrategyType]);


    const runParamOptimisation = async () => {
        if (!strategySelectResults) return;
        setIsLoading(true);
        setUploadComplete(false);
        setProgress({});
        setFilterResults(null);
        setError(null);
    }

    return {
        paramValues,
        setParamValues,
        filterResults,
        runParamOptimisation,
        isLoading,
        error,
        strategyType,
        uploadComplete,
        progress
    }
}