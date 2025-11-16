import { useState, useEffect } from "react";
import { filters } from "../params/preScreenFilters"
import { getApiUrl } from "../../../utils/apiUrl";


export function usePreScreen(uniFilterResults, endDate, setVisible) {
    const [uploadComplete, setUploadComplete] = useState(true);
    const [testingComplete, setTestingComplete] = useState(true);
    const [filterValues, setFilterValues] = useState({});
    const [filterResults, setFilterResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState({ testing: 0, completed: 0, total: 0 });
    const [fails, setFails] = useState({})

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


    useEffect(() => {
        setFilterResults(null);
        setVisible(false);
        setFails({});
    }, [uniFilterResults, setVisible])

    const preScreen = async () => {
        if (!uniFilterResults) return;
        const symbols = uniFilterResults.map(s => s.value);
        if (!symbols.length) return;

        setFilterResults(null)
        setFails({});
        setUploadComplete(false);
        setIsLoading(true);

        const end = new Date(endDate.value);
        const start = new Date(end);
        start.setFullYear(end.getFullYear() - 3);

        const startStr = start.toISOString().split("T")[0].replace(/-/g, "-");
        try {
            // 1️⃣ Sync ingest
            const ingestRes = await fetch(`${getApiUrl()}/api/data/ohlcv/syncIngest/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbols, start: startStr, end: endDate.value }),
            });
            await ingestRes.json();
            setUploadComplete(true);
        } catch (err) {
            console.error(err);
            setError(err);
            setIsLoading(false);
            alert("Data ingestion failed");
            return;
        }

        const filterDict = Object.fromEntries(
            Object.entries(filterValues).flatMap(([key, arr]) => 
                arr.map(f => [f.name, f.value])
            )
        );

        setTestingComplete(false);
        setProgress({ completed: 0, total: symbols.length });

        try {
            // 2️⃣ Start pre-screen
            const res = await fetch(`${getApiUrl()}/api/portfolio/runPreScreen/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbols, start: startStr, end: endDate.value, filters: filterDict }),
            });
            const { task_id } = await res.json();

            // 3️⃣ SSE for progress
            const evtSource = new EventSource(`${getApiUrl()}/api/portfolio/streamProgress/${task_id}`);
            evtSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setProgress(data);
                if (data.completed >= data.total) {
                    // 4️⃣ Fetch final results
                    fetch(`${getApiUrl()}/api/portfolio/getPreScreenResults/${task_id}`)
                        .then(res => res.json())
                        .then(results => {
                            const { symbols = {}, failed_count = {} } = results;
                            setFilterResults(
                                Object.fromEntries(
                                    Object.entries(symbols)
                                    .filter(([_, r]) => {
                                        const { global, ...rest } = r;
                                        return global && Object.values(rest).some(Boolean);
                                    })
                                    .map(([sym, r]) => {
                                        const { global, ...rest } = r;
                                        return [
                                            sym,
                                            Object.entries(rest)
                                                .filter(([, val]) => val)
                                                .map(([group]) => group)
                                        ];
                                    })
                                )
                            );
                            setFails(failed_count || {})
                            setTestingComplete(true);
                            setIsLoading(false);
                            evtSource.close();
                        })
                }
            };
        } catch (err) {
            alert("Pre-screen failed");
            setIsLoading(false);
            setError(err);
            console.error(err)
            return;
        }
    };

    return {
        filterValues,
        setFilterValues,
        filterResults,
        preScreen,
        isLoading,
        error,
        uploadComplete,
        testingComplete,
        progress,
        fails
    };
}
