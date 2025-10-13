import { regionOptions, sectorOptions } from "./uniFilterOptions"

export const filters = {
    regionFilter: {
        name: "regions",
        label: "Choose Regions",
        type: "categorical",
        options: regionOptions,
        description: "",
        default: ["us"],
    },
    exchangeFilter: {
        name: "exchanges",
        label: "Choose Exchanges",
        type: "categorical",
        options: [],
        description: "",
        default: ["NMS", "NYQ"],
    },
    sectorFilter: {
        name: "sectors",
        label: "Choose Sectors",
        type: "categorical",
        options: sectorOptions,
        description: "",
        default: [],
    },
    industryFilter: {
        name: "industries",
        label: "Choose Industries",
        type: "categorical",
        options: [],
        description: "",
        default: []
    },
    liquidityFilter: {
        name: "min_daily_vol",
        label: "Min Average Daily Volume",
        type: "number",
        description: "",
        default: 500000,
    },
    marketCapFilter: {
        name: "min_market_cap",
        label: "Min Market Cap",
        type: "number",
        description: "",
        default: 1000000000,
    },
    epsFilter: {
        name: "min_eps_growth",
        label: "Min EPS Growth",
        type: "number",
        description: "",
        default: 0,
    },
    priceEarningsFilter: {
        name: "max_price_earnings_ratio",
        label: "Max Price/Earnings Ratio",
        type: "number",
        description: "",
        default: 50,
    }
}