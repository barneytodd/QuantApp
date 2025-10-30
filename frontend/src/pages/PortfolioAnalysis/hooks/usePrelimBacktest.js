import { useState, useEffect, useRef } from "react";
import { filters } from "../params/prelimBacktestFilters"
import { strategies } from "../../Backtesting/parameters/strategyRegistry";
import { useStrategyParams } from "../../Backtesting/hooks/useStrategyParams";
import { usePairs } from "../../Backtesting/hooks/usePairs"

export function usePrelimBacktest(preScreenResults, startDate, endDate, setVisible) {
    const [filterValues, setFilterValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const runningSelectRef = useRef(0);

    const [allSymbols, setAllSymbols] = useState([]);
    const [start, setStart] = useState(null);
    const [selectStart, setSelectStart] = useState(null);
    const [end, setEnd] = useState(null);
   
    
    const { 
        selectedPairs, 
        selectPairs, 
        progress: pairsProgress,
        isLoading: pairsLoading, 
        error: pairsError 
    } = usePairs();

    const {
        strategyType,
        setStrategyType,
        basicParams,
        advancedParams,
    } = useStrategyParams(allSymbols, selectedPairs);

    // set default filters
    useEffect(() => {
        const filterDefaults = Object.fromEntries(
            Object.values(filters).map((f) => {
                const { default: value, name, ...rest } = f;
                return [name, { value, ...rest }];
            })
        );
        setFilterValues(filterDefaults);
    }, [])

    //set date range
    useEffect(() => {
        if (endDate.value && startDate.value) {
            const end_ = new Date(endDate.value);
            const start_ = new Date(end_);
            const selectStart = new Date(startDate.value)
            start_.setFullYear(end_.getFullYear() - 1);

            const startStr = start_.toISOString().split("T")[0].replace(/-/g, "-");
            const selectStartStr = selectStart.toISOString().split("T")[0].replace(/-/g, "-");
            const endStr = end_.toISOString().split("T")[0].replace(/-/g, "-");
            setStart(startStr);
            setSelectStart(selectStartStr);
            setEnd(endStr);
        }
    }, [endDate, startDate])

    useEffect(() => {
        setFilterResults(null);
        setVisible(false);
        setError(null);
        if (preScreenResults && runningSelectRef.current === 0) {
            runningSelectRef.current += 1;

            const symbols = Object.keys(preScreenResults);
            setAllSymbols(symbols);
            
            const meanReversionSyms = Object.entries(preScreenResults)
                .filter(([_, strategies]) => strategies.includes("mean_reversion"))
                .map(([symbol, _]) => symbol);
                
            const run = async () => {
                try {
                    await selectPairs(meanReversionSyms, selectStart, end); 
                    runningSelectRef.current = 0;
                }
                catch(err) {
                    alert("pair Selection Failed");
                    setError(err);
                }
            };

            run();            
        }
        
    }, [preScreenResults, setVisible, selectPairs, selectStart, end])


    useEffect(() => {
        if (allSymbols.length > 0 && strategyType?.value !== "custom") {
            setStrategyType({value: "custom", label: "custom"});
        }
    }, [allSymbols, strategyType, setStrategyType]);

    const runPrelimBacktest = async () => {
        if (!preScreenResults) return;
        setFilterResults(null)
        try {
            setIsLoading(true);
            const symbolItems = [
                ...Object.entries(preScreenResults).flatMap(
                ([symbol, types]) =>
                    // for each type, find all strategies that match that type
                    types.flatMap(type =>
                        Object.entries(strategies)
                            .filter(([_, strategyObj]) => strategyObj.type === type)
                            .map(([strategyName, _]) => ({
                                symbols: [symbol],
                                strategy: strategyName,
                                weight: 1
                            }))
                    )
                ),

                ...selectedPairs.map((pair) => ({
                        symbols: [pair.stock1, pair.stock2],
                        strategy: "pairs_trading",
                        weight: 1
                    })
                ),
            ];

            const params = Object.fromEntries(
            Object.entries(advancedParams)
                .filter(([key, _]) => !key.endsWith("_weight"))
                .map(([k, v]) => [
                    k, 
                    { 
                        value: k === "startDate" ? start : k === "endDate" ? end : v.value, 
                        lookback: v.lookback ?? false 
                    }
                ])
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
            const symbolStrategies = data
                .filter(item => item.metrics?.sharpe_ratio > filterValues?.sharpe?.value && item.symbol !== "overall")
                .reduce((acc, item) => {
                    if (!acc[item.symbol]) {
                        acc[item.symbol] = [];
                    }
                    acc[item.symbol].push(item.strategy);
                    return acc;
                }, {});
            setFilterResults({...symbolStrategies});
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
        runPrelimBacktest,
        isLoading,
        error,
        pairsLoading,
        pairsError,
        pairsProgress,
        strategyType
    }
}