import { useState, useEffect } from "react";
import { filters } from "../params/prelimBacktestFilters"
import { strategies } from "../../Backtesting/parameters/strategyRegistry";
import { useStrategyParams } from "../../Backtesting/hooks/useStrategyParams";
import { usePairs } from "../../Backtesting/hooks/usePairs"

export function usePrelimBacktest(preScreenResults, setVisible) {
    const [filterValues, setFilterValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [startSelect, setStartSelect] = useState(false);

    const [allSymbols, setAllSymbols] = useState([]);
    const [momentumSymbols, setMomentumSymbols] = useState([])
    
    const { 
        selectedPairs, 
        setSelectedPairs,
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

    useEffect(() => {
        setFilterResults(null);
        setVisible(false);
        setMomentumSymbols([])
        if (preScreenResults) {
            const symbols = Object.keys(preScreenResults);
            setAllSymbols(symbols);
            
            const momentumSyms = Object.entries(preScreenResults)
            .filter(([symbol, strategies]) => strategies.includes("mean_reversion"))
            .map(([symbol]) => symbol);
            setMomentumSymbols(momentumSyms)

            if (momentumSyms.length >= 2) {
                setStartSelect(true);
            }
            else setSelectedPairs([]);
        }
        else {
            setStartSelect(false);
        }
    }, [preScreenResults, setVisible, setSelectedPairs])

    // set pairs and symbols
    useEffect(() => {
        if (!startSelect || !momentumSymbols) return;

        (async () => await selectPairs(momentumSymbols))();
       
        setStartSelect(false);
    }, [startSelect, momentumSymbols, selectPairs]);


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
                            .filter(([strategyName, strategyObj]) => strategyObj.type === type)
                            .map(([strategyName, strategyObj]) => ({
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