import { useState, useEffect } from "react";
import { useOptimisation } from "../../Backtesting/hooks/useOptimisation";
import { useOptimisationParams } from "../../Backtesting/hooks/useOptimisationParams";
import { params } from "../params/paramOptimisationParams"

export function useParamOptimisation(strategySelectResults, setVisible) {
    const [progress, setProgress] = useState({});
    const [scoringParams, setScoringParams] = useState({});
    const { optimParams } = useOptimisationParams()

    const { 
        optimisationResult, 
        setOptimisationResult,
        optimiseParameters, 
        isLoading: optimLoading, 
        error: optimError 
    } = useOptimisation();

    useEffect(() => {
        const scoringParamDefaults = Object.fromEntries(
            Object.values(params).map((param) => {
                const { default: value, name, ...rest } = param;
                return [name, { value, ...rest }];
            })
        )
        setScoringParams(scoringParamDefaults)
    }, [])

    useEffect(() => {
        setVisible(false);
        setOptimisationResult(null);
        setProgress({});
    }, [strategySelectResults, setVisible, setOptimisationResult])


    const runParamOptimisation = async () => {
        if (!strategySelectResults || Object.keys(strategySelectResults).length === 0) {
            console.warn("No strategy selection results provided");
            return;
        }

        const strategyTypesWithSymbols = Object.entries(strategySelectResults)
            .reduce((acc, [symbol, { strategy, score }]) => {
                if (!acc[strategy]) acc[strategy] = [];
                acc[strategy].push({
                    symbols: symbol.split("-"),
                    strategy,
                    weight: 1 // or you can use score if you want weighted importance
                });
                return acc;
            }, {});
        
        const scoringParamValues = Object.fromEntries(
            Object.entries(scoringParams).map(([name, param]) => [
                name,
                param.value
            ])
        )

        await optimiseParameters({ strategyTypesWithSymbols, optimParams, scoringParamValues })
    }

    return {
        scoringParams,
        setScoringParams,
        optimisationResult,
        runParamOptimisation,
        optimLoading,
        optimError,
        progress
    }
}