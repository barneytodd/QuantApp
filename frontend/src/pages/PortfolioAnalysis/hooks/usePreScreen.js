import { useState, useEffect } from "react";
import { filters } from "../filters/preScreenFilters"

export function usePreScreen() {
    const [uploadComplete, setUploadComplete] = useState(true);
    const [testingComplete, setTestingComplete] = useState(true);
    const [filterValues, setFilterValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // default filters
    useEffect(() => {
        if (!filters) return;
        const filterDefaults = Object.fromEntries(
            Object.entries(filters).map(([key, arr]) => [
            key,
            arr.map(f => {
                const { default: value, ...rest } = f;
                return { value, ...rest };
            })
            ])
        );
        setFilterValues(filterDefaults);
    }, []);


    const preScreen = async (uniFilterResults) => {
        if (!uniFilterResults) return;

        const symbols = uniFilterResults.map(s => s.value)
        if (symbols.length === 0) return;

        setUploadComplete(false);
        setIsLoading(true);

        const today = new Date();
        const start = new Date();
        start.setFullYear(today.getFullYear() - 3)

        const todayStr = today.toISOString().split("T")[0].replace(/-/g, "-");
        const startStr = start.toISOString().split("T")[0].replace(/-/g, "-");

        try {
            const res = await fetch("http://localhost:8000/api/data/ohlcv/syncIngest/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbols: symbols, start: startStr, end: todayStr }),
            });
            const data = await res.json();
            if (data) setUploadComplete(true);
        } catch (err) {
            console.error(err);
            alert("Error uploading data to db");
        }

        const filterDict = Object.fromEntries(
            Object.entries(filterValues).flatMap(([key, arr]) => 
                arr.map(f => [f.name, f.value])
            )
        );
        
        setTestingComplete(false);
        console.log(symbols)

        try {
            const res = await fetch("http://localhost:8000/api/portfolio/runPreScreen/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbols: symbols, start: startStr, end: todayStr, filters: filterDict }),
            });
            const data = await res.json();
            if (data) setTestingComplete(true);
            console.log(data)
            setFilterResults(
                Object.fromEntries(
                    Object.entries(data)
                    .filter(([_, results]) => {
                        const { global, ...rest } = results;
                        const otherPassed = Object.values(rest).some(Boolean);
                        return global && otherPassed; // only keep if global and another true
                    })
                    .map(([sym, results]) => [
                        sym,
                        Object.entries(results)
                        .filter(([, result]) => result)
                        .map(([group]) => group)
                    ])
                )
            );
        } catch (err) {
            console.error(err);
            alert("Error running pre-screen");
        } finally {
            setIsLoading(false)
        }
    }
    
    return {
        filterValues,
        setFilterValues,
        filterResults,
        preScreen,
        isLoading,
        error,
        uploadComplete,
        testingComplete
    }
}