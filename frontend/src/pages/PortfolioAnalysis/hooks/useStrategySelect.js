import { useState, useEffect, useMemo } from "react";
import { params } from "../params/strategySelectParams"
import { useStrategyParams } from "../../Backtesting/hooks/useStrategyParams";

export function useStrategySelect(prelimBacktestResults, startDate, endDate, setVisible) {
    const [paramValues, setParamValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [metricRanges, setMetricRanges] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [uploadComplete, setUploadComplete] = useState(true);
    const [progress, setProgress] = useState({});

    const allSymbols = useMemo(
        () => [
            ...new Set(
            Object.keys(prelimBacktestResults ?? {}).flatMap((s) => s.split("-"))
            )
        ],
        [prelimBacktestResults]
    )

    const selectedPairs = useMemo(
        () => Object.keys(prelimBacktestResults ?? {})
                .filter((s) => s.includes("-"))
                .map((s) => ({
                    "stock1": s.split("-")[0],
                    "stock2": s.split("-")[1]
                })), 
        [prelimBacktestResults]
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
    }, [prelimBacktestResults, setVisible])

    useEffect(() => {
        if (allSymbols.length > 0 && strategyType?.value !== "custom") {
            setStrategyType({value: "custom", label: "custom"});
        }
    }, [allSymbols, selectedPairs, strategyType, setStrategyType]);


    const computeMetricRanges = (results) => {
        const metrics = ["sharpe", "cagr", "maxDrawdown", "winRate"];
        const ranges = {};

        metrics.forEach((m) => {
            const values = Object.values(results)
            .flatMap((symbolData) =>
                Object.values(symbolData).map((s) => s[m]).filter((v) => v !== undefined)
            );

            const min = Math.min(...values);
            const max = Math.max(...values);
            ranges[m] = { min, max };
        });
        setMetricRanges(ranges);
        return ranges;
    };


    const normaliseMetric = (value, min, max, invert = false) => {
        if (value === undefined || isNaN(value)) return 0;
        if (max === min) return 0.5; // avoid divide-by-zero
        const norm = (value - min) / (max - min);
        return invert ? 1 - norm : norm;
    };


    const chooseStrategy = (results) => {
        const bestBySymbol = {};
        const ranges = computeMetricRanges(results);


        Object.entries(results).forEach(([symbol, strategyResults]) => {

            let bestStrategy = null;
            let bestScore = -Infinity;
            
            Object.entries(strategyResults).forEach(([strategy, res]) => {
                const sharpeNorm = normaliseMetric(res.sharpe, ranges.sharpe.min, ranges.sharpe.max);
                const cagrNorm = normaliseMetric(res.cagr, ranges.cagr.min, ranges.cagr.max);
                const ddNorm = normaliseMetric(res.maxDrawdown, ranges.maxDrawdown.min, ranges.maxDrawdown.max, true);
                const winRateNorm = normaliseMetric(res.winRate, ranges.winRate.min, ranges.winRate.max);

                const score =
                    sharpeNorm * (paramValues?.sharpe?.value ?? 1) +
                    cagrNorm * (paramValues?.cagr?.value ?? 1) +
                    ddNorm * (paramValues?.maxDrawdown?.value ?? 1) +
                    winRateNorm * (paramValues?.winRate?.value ?? 1);

                if (score > bestScore) {
                    bestScore = score;
                    bestStrategy = {strategy: strategy, score: score};
                }
            });
            bestBySymbol[symbol] = bestStrategy;
        })
        
        const bestResults = Object.fromEntries(
            Object.entries(bestBySymbol).filter(([_, strategy]) => strategy.score >= paramValues?.scoringThreshold)
        )
        return bestResults
    }

    const chooseSingleOrPair = (bestResults) => {
        const finalResults = {...bestResults}
        const pairSymbols = Object.keys(bestResults).filter((s) => s.includes("-"));
        pairSymbols.forEach((pair) => {
            const [stock1, stock2] = pair.split("-");

            const pairResult = bestResults[pair];
            const singleA = bestResults[stock1];
            const singleB = bestResults[stock2];

            // Combine individual scores (equal weighting)
            const combinedIndividualScore = 
                singleA && singleB 
                    ? 0.5 * (singleA.score + singleB.score) : singleA 
                        ? singleA.score : singleB 
                            ? singleB.score : -Infinity;

            // Compare pair vs. individuals
            if (pairResult.score > combinedIndividualScore) {
                // Pair performs better → keep pair, remove singles
                if (finalResults[stock1]) delete finalResults[stock1];
                if (finalResults[stock2]) delete finalResults[stock2];
            } else {
                // Individuals perform better → remove pair
                delete finalResults[pair];
            }
        });

        return finalResults;
    };

    const runStrategySelect = async () => {
        if (!prelimBacktestResults) return;
        setIsLoading(true);
        setUploadComplete(false);
        setProgress({});
        setFilterResults(null);
        setError(null);

        const today = new Date();
        const todayStr = today.toISOString().split("T")[0].replace(/-/g, "-");

        try {
            // 1️⃣ Sync ingest
            const ingestRes = await fetch("http://localhost:8000/api/data/ohlcv/syncIngest/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbols: allSymbols, start: startDate.value, end: todayStr }),
            });
            await ingestRes.json();
            setUploadComplete(true);
        } catch (err) {
            console.error(err);
        }

        try {
            const symbolItems = Object.entries(prelimBacktestResults)
                .flatMap(
                    ([symbol, strategies]) =>
                        strategies.map((s) => ({
                            symbols: symbol.split("-"),
                            strategy: s,
                            weight: 1
                        })
                    )
                );
            
            const updatedAdvancedParams = {
                ...advancedParams,
                startDate: { ...advancedParams.startDate, value: startDate.value },
                endDate: { ...advancedParams.endDate, value: endDate.value }
            };

            const params = Object.fromEntries(
                Object.entries(updatedAdvancedParams)
                    .filter(([key, _]) => !key.endsWith("_weight"))
                    .map(([k, v]) => [k, { value: v.value, lookback: v.lookback ?? false }])
                    .concat(
                        Object.entries(basicParams).map(([k, v]) => [k, { value: v.value, lookback: v.lookback ?? false }])
                    )
            )

            // 2️⃣ Start walk-forward backtest task
            const startRes = await fetch("http://localhost:8000/api/strategies/backtest/walkforward/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbolItems, params }),
            });
            const { task_id } = await startRes.json();

            if (!task_id) {
                throw new Error("No task_id returned from backend");
            }

            // 3️⃣ Stream progress via SSE
            await new Promise((resolve, reject) => {
                const evtSource = new EventSource(`http://localhost:8000/api/strategies/backtest/walkforward/stream/${task_id}`);
                evtSource.onmessage = (e) => {
                    const data = JSON.parse(e.data);
                    // You can store per-segment progress in state if needed
                    setProgress(data)

                    if (data.status === "done") {
                        evtSource.close();
                        resolve();
                    }
                };
                evtSource.onerror = (err) => {
                    console.error("SSE error:", err);
                    evtSource.close();
                    reject(err);
                };
            });

            // 4️⃣ Fetch aggregated results once done
            const aggRes = await fetch(`http://localhost:8000/api/strategies/backtest/walkforward/results/${task_id}`);
            if (!aggRes.ok) throw new Error("Failed to fetch aggregated results");
            const data = await aggRes.json();
            console.log(data.aggregated_results)
            const symbolResults = data.aggregated_results
                .filter(item => item.symbol !== "overall")
                .reduce((acc, item) => {
                    if (!acc[item.symbol]) {
                        acc[item.symbol] = {};
                    }
                    acc[item.symbol][item.strategy] = {
                            sharpe: item.avgSharpe,
                            cagr: item.avgCAGR,
                            maxDrawdown: item.avgMaxDrawdown,
                            winRate: item.avgWinRate
                        }
                    return acc;
                }, {});
            console.log(symbolResults)
            const strategyBySymbol = chooseStrategy(symbolResults)
            console.log(strategyBySymbol)
            const finalResults = chooseSingleOrPair(strategyBySymbol)
            console.log(finalResults)
            setFilterResults(finalResults);
            return data;
        } catch (err) {
            setError(err);
            alert("Backtest failed");
        } finally {
            setIsLoading(false);
        }
    }

    return {
        paramValues,
        setParamValues,
        filterResults,
        metricRanges,
        runStrategySelect,
        isLoading,
        error,
        strategyType,
        uploadComplete,
        progress
    }
}