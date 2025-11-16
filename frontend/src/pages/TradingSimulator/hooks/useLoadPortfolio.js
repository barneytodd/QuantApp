import { useState, useEffect } from "react";
import { getApiUrl } from "../../../utils/apiUrl";


export function useLoadPortfolios() {
    const [availablePortfolios, setAvailablePortfolios] = useState([]);
    const [getPortoliosLoading, setGetPortfoliosLoading] = useState(false);
    const [getPortfoliosError, setGetPortfoliosError] = useState(null);

    useEffect(() => {
        try {
            setGetPortfoliosLoading(true);
            fetch(`${getApiUrl()}/api/portfolio/list`)
                .then((res) => res.json())
                .then((data) => setAvailablePortfolios(
                    data.map(p => ({
                        value: p, 
                        label: `${p.meta?.start}–${p.meta?.end}`
                    }))
                ));
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