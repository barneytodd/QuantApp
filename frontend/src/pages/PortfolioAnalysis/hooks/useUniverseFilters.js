import { useState, useEffect } from "react";
import { filters } from "../params/universeFilters";
import { exchangeOptions, industryOptions } from "../params/uniFilterOptions"

export function useUniverseFilters() {
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

    useEffect(() => {
        const selectedRegions = filterValues.regions?.value || [];
        const newExchangeOptions = selectedRegions.flatMap(
            (region) => exchangeOptions[region] || []
        );

        setFilterValues((prev) => {
            const oldValue = prev.exchanges?.value
            const newValue = (oldValue.length > 0 ? oldValue : filters.exchangeFilter.default).filter((v) =>
                newExchangeOptions.includes(v)
            );

            return {
            ...prev,
            "exchanges": {
                ...prev.exchanges,
                options: newExchangeOptions,
                value: newValue
            }
            };
        });
    }, [filterValues.regions?.value]);

    useEffect(() => {
        const selectedSectors = filterValues.sectors?.value || [];
        const newIndustryOptions = selectedSectors.flatMap(
            (region) => industryOptions[region] || []
        );

        setFilterValues((prev) => {
            const oldValue = prev.industries?.value
            const newValue = (oldValue.length > 0 ? oldValue : filters.industryFilter.default).filter((v) =>
                newIndustryOptions.includes(v)
            );

            return {
            ...prev,
            "industries": {
                ...prev.industries,
                options: newIndustryOptions,
                value: newValue
            }
            };
        });
    }, [filterValues.sectors?.value]);

    const filterUniverse = async() => {
        setIsLoading(true);
        setError(null);
        const payload = Object.fromEntries(Object.entries(filterValues).map(([name, filter]) => [name, filter.value]))
        try {
            const res = await fetch("http://localhost:8000/api/symbols/fetch_symbols", {
                method: "POST",
                headers: {
                "Content-Type": "application/json",
                },
                body: JSON.stringify({filters:payload}), // empty payload
            })
            const result = await res.json();
            setFilterResults(result.map(s => ({ value: s, label: s })))
        } catch (err) {
            console.error(err);
            setError(err);
            alert("Error fetching filtered symbols");
        } finally {
            setIsLoading(false);
        }
    };

    return {
        filterValues,
        setFilterValues,
        filterResults,
        filterUniverse,
        isLoading,
        error
    };
}
