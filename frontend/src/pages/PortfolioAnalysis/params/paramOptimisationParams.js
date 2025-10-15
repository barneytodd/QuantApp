export const params = {
    sharpe: {
        name: "sharpe",
        label: "Sharpe Ratio",
        type: "number",
        default: 0.4,
        info: "Set weighting for sharpe ratio in the combined metric used to optimise parameters"
    },
    cagr: {
        name: "cagr",
        label: "CAGR",
        type: "number",
        default: 0.3,
        info: "Set weighting for compound annual growth rate in the combined metric used to optimise parameters"
    },
    maxDrawdown: {
        name: "maxDrawdown",
        label: "Max Drawdown",
        type: "number",
        default: 0.2,
        info: "Set weighting for max drawdown in the combined metric used to optimise parameters"
    },
    winRate: {
        name: "winRate",
        label: "Win Rate",
        type: "number",
        default: 0.1,
        info: "Set weighting for trade win rate in the combined metric used to optimise parameters"
    }
}