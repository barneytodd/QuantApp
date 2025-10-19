import { useState, useEffect } from "react";
import { params } from "../params/portfolioWeightsParams"

export function usePortfolioWeights(paramOptimisationResults, setVisible) {
    const [portfolioWeightsParams, setPortfolioWeightsParams] = useState({});
    const [portfolioWeightsResult, setPortfolioWeightsResult] = useState(null);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [loadingInputs, setLoadingInputs] = useState(false);
    const [loadingHrp, setLoadingHrp] = useState(false);
    const [loadingOptimisation, setLoadingOptimisation] = useState(false);

    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    

    useEffect(() => {
        const portfolioWeightsParamDefaults = Object.fromEntries(
            Object.values(params).map((param) => {
                const { default: value, name, ...rest } = param;
                return [name, { value, ...rest }];
            })
        )

        setPortfolioWeightsParams(portfolioWeightsParamDefaults)
    }, [])


    useEffect(() => {
        setVisible(false);
        setPortfolioWeightsResult(null);
        setError(null);
        setSaved(false);
    }, [paramOptimisationResults, setVisible, setPortfolioWeightsResult])

    const buildPortfolio = async (weights, parameters) => {
        const portfolio = Object.fromEntries(
            Object.entries(parameters).map(([strat, paramResults]) => [
                strat,
                {
                    "symbols": paramResults.aggregated_results.map((symbolInfo) => ({
                        "symbol": symbolInfo.symbol,
                        "weight": weights[symbolInfo.symbol]
                    })),
                    "params": paramResults.best_params
                }
            ])
        );
        return portfolio;
    };
    


    const runPortfolioWeights = async () => {
        if (!paramOptimisationResults || Object.keys(paramOptimisationResults).length === 0) {
            console.warn("No parameter optimisation results provided");
            return;
        }
        
        setPortfolioWeightsResult(null);
        setIsLoading(true);
        setSaved(false);

        // 1. estimate returns and risk
            // for now use backtest results weighted to give more weight to recent results
            // later apply a better model
        let inputData;
        try {
            setLoadingInputs(true);

            const returns = Object.fromEntries(
                Object.entries(paramOptimisationResults).flatMap(([_, strat_results]) => 
                    strat_results.aggregated_results.map((result) => [
                        result.symbol,
                        result.returns
                    ])
                )
            )

            const response = await fetch("http://localhost:8000/api/portfolio/inputs", {
                method: "POST",
                headers: {
                "Content-Type": "application/json"
                },
                body: JSON.stringify( {returns, ewma_decay: portfolioWeightsParams.ewma_decay.value} )
            });

            if (!response.ok) {
                alert("Failed to compute portfolio inputs");
                setLoadingInputs(false);
                setIsLoading(false);
                setError(true);
                return;
            }

            inputData = await response.json();

        } catch (err) {
            setError(err);
            alert("Failed to compute portfolio inputs");
        } finally {
            setLoadingInputs(false);
        }


        // 2. HRP
        let hrpData;
        try { 
            setLoadingHrp(true);

            const response = await fetch("http://localhost:8000/api/portfolio/hrp", {
                method: "POST",
                headers: {
                "Content-Type": "application/json"
                },
                body: JSON.stringify( {riskMatrix: inputData.risk_matrix} )
            });

            if (!response.ok) {
                alert("Failed to complete hrp allocation");
                setIsLoading(false);
                setLoadingHrp(false);
                setError(true);
                return;
            }

            hrpData = await response.json();

        } catch (err) {
            setError(err);
            alert("Failed to complete hrp allocation");
        } finally {
            setLoadingHrp(false);
        }   
     
        
        // 3. formulate objective, apply costraints, solve optimisation
        let portfolio;
        try { 
            setLoadingOptimisation(true);

            const optimisationParams = Object.fromEntries(
                Object.entries(portfolioWeightsParams).filter(([_, param]) => param.group === "optimisation")
            )
            
            if (inputData.risk_matrix.symbols.length * optimisationParams.max_weight.value < 1) {
                alert("Max Weight too small - weights cannot add to 1");
                setError(true);
                setLoadingOptimisation(false);
                setIsLoading(false);
                return;
            }

            console.log(optimisationParams);

            const payload = {
                "expected_returns": inputData.expected_returns,
                "risk_matrix": inputData.risk_matrix,
                "baseline_weights": hrpData.weights,
                "params": optimisationParams
            }

            console.log(payload)

            const response = await fetch("http://localhost:8000/api/portfolio/optimise", {
                method: "POST",
                headers: {
                "Content-Type": "application/json"
                },
                body: JSON.stringify( payload )
            });

            if (!response.ok) {
                alert("Failed to optimise");
                setError(true);
                setLoadingOptimisation(false);
                setIsLoading(false);
                return;
            }

            const optimisationData = await response.json();
            portfolio = await buildPortfolio(optimisationData.weights, paramOptimisationResults)
            setPortfolioWeightsResult(portfolio)

        } catch (err) {
            setError(err);
            setLoadingOptimisation(false);
            setIsLoading(false);
            alert("Failed to optimise");
        } finally {
            setLoadingOptimisation(false);
            setIsLoading(false);
        }        
    }

    const savePortfolioToDB = async (portfolio, metadata = {}) => {
        if (!portfolio || Object.keys(portfolio).length === 0) {
            alert("No portfolio provided")
            return;
        }
        
        setSaving(true);
        setSaved(false);
        try {
            console.log(portfolio)
            const response = await fetch("http://localhost:8000/api/portfolio/save", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify( {portfolio} )
            });

            if (!response.ok) {
                const text = await response.text();
                console.error("Failed to save portfolio:", text);
                setSaving(false);
                alert("Failed to save portfolio to database");
                return false;
            }

            const data = await response.json();
            console.log("Portfolio saved successfully:", data);
            return true;

        } catch (err) {
            console.error("Error saving portfolio:", err);
            setSaving(false);
            alert("Error saving portfolio to database");
            return false;
        } finally {
            setSaving(false);
            setSaved(true);
        }
    };

    return {
        portfolioWeightsParams,
        setPortfolioWeightsParams,
        portfolioWeightsResult,
        runPortfolioWeights,
        isLoading,
        loadingInputs,
        loadingHrp,
        loadingOptimisation,
        error,
        savePortfolioToDB,
        saving,
        saved
    }
}