import { useState, useEffect, useRef } from "react";
import { useOptimisation } from "../../Backtesting/hooks/useOptimisation";
import { params } from "../params/paramOptimisationParams"

const server = process.env.REACT_APP_ENV === "local" ? "localhost" : "backend";
const API_URL = `http://${server}:${process.env.REACT_APP_BACKEND_PORT}`;

export function useParamOptimisation(strategySelectResults, metricRanges, startDate, endDate, setVisible) {
    const [optimisationParams, setOptimisationParams] = useState({});
    const [progress, setProgress] = useState({});
    const [portfolio, setPortfolio] = useState({});
    const evtSourceRef = useRef(null);
    

    const { 
        optimisationResult, 
        setOptimisationResult,
        optimiseParameters, 
        isLoading: optimLoading, 
        error: optimError 
    } = useOptimisation(startDate, endDate);

    useEffect(() => {
        const optimisationParamDefaults = Object.fromEntries(
            Object.values(params).map((param) => {
                const { default: value, name, ...rest } = param;
                return [name, { value, ...rest }];
            })
        )

        setOptimisationParams(optimisationParamDefaults)
    }, [])


    useEffect(() => {
        setVisible(false);
        setOptimisationResult(null);
        setProgress({});
        return () => {
            if (evtSourceRef.current) {
                evtSourceRef.current.close();
            }
        };
    }, [strategySelectResults, setVisible, setOptimisationResult])

    useEffect(() => {
        if (!optimisationResult || !strategySelectResults) return;
        const totalSymbols = Object.keys(strategySelectResults).length;
        const globalWeight = 1 / totalSymbols;

        // Group by strategy
        const symbols = Object.entries(strategySelectResults).reduce((acc, [symbol, info]) => {
            if (!acc[info.strategy]) acc[info.strategy] = [];
            acc[info.strategy].push({ symbol, weight: globalWeight });
            return acc;
        }, {});

        const result = Object.fromEntries(
            Object.entries(symbols).map(([strat, syms]) => [
                strat, 
                {symbols: syms, params: optimisationResult[strat].best_params}
            ])
        )
        setPortfolio(result)
    }, [optimisationResult, strategySelectResults])

    const runParamOptimisation = async () => {
        if (evtSourceRef.current) {
            console.warn("Optimisation already running.");
            evtSourceRef.current.close();
            evtSourceRef.current = null
            return;
        }

        if (!strategySelectResults || Object.keys(strategySelectResults).length === 0) {
            console.warn("No strategy selection results provided");
            return;
        }
        setOptimisationResult(null);
        setProgress({});

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
            Object.entries(optimisationParams)
                .filter(([_, param]) => param.group === "scoringParams")
                .map(([name, param]) => [
                    name,
                    param.value
                ])
        )

        evtSourceRef.current = new EventSource(
            `${API_URL}/api/params/optimisation/stream`
        );

        evtSourceRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.done) {
                if (evtSourceRef.current) {
                    evtSourceRef.current.close();
                    evtSourceRef.current = null;
                }
                return;
            }

            setProgress(data);
            };

        evtSourceRef.current.onerror = () => {
            if (evtSourceRef.current) {
                evtSourceRef.current.close();
                evtSourceRef.current = null;
            }
        };

        try {
            await optimiseParameters({ strategyTypesWithSymbols, optimParams: optimisationParams, scoringParams: scoringParamValues, metricRanges })
        }
        catch {
            setProgress({});
        }
        finally {
            if (evtSourceRef.current) {
                evtSourceRef.current.close();
                evtSourceRef.current = null;
            }
        }
        setProgress({});
    }

    return {
        optimisationParams,
        setOptimisationParams,
        optimisationResult,
        runParamOptimisation,
        optimLoading,
        optimError,
        progress, 
        portfolio
    }
}