import { useState, useEffect } from "react";

export function useLoadPortfolios() {
    const [availablePortfolios, setAvailablePortfolios] = useState([]);
    const [getPortoliosLoading, setGetPortfoliosLoading] = useState(false);
    const [getPortfoliosError, setGetPortfoliosError] = useState(null);

    useEffect(() => {
        try {
            setGetPortfoliosLoading(true);
            fetch("http://localhost:8000/api/portfolio/list")
                .then((res) => res.json())
                .then((data) => setAvailablePortfolios(data.map(p => ({value: p, label: p.created_at}))));
        } catch (err) {
            setGetPortfoliosError(err)
            alert("Failed to fetch portfolios from db");
        } finally {
            setGetPortfoliosLoading(false);
        }
    }, [])

    return {
        availablePortfolios,
        getPortoliosLoading,
        getPortfoliosError
    }
}