export const params = {
    sharpe: {
        name: "sharpe",
        label: "Sharpe Ratio",
        type: "number",
        group: "scoringParams",
        default: 0.4,
        info: "Set weighting for sharpe ratio in the combined metric used to compare strategies"
    },
    cagr: {
        name: "cagr",
        label: "CAGR",
        type: "number",
        group: "scoringParams",
        default: 0.3,
        info: "Set weighting for compound annual growth rate in the combined metric used to compare strategies"
    },
    maxDrawdown: {
        name: "maxDrawdown",
        label: "Max Drawdown",
        type: "number",
        group: "scoringParams",
        default: 0.2,
        info: "Set weighting for max drawdown in the combined metric used to compare strategies"
    },
    winRate: {
        name: "winRate",
        label: "Win Rate",
        type: "number",
        group: "scoringParams",
        default: 0.1,
        info: "Set weighting for trade win rate in the combined metric used to compare strategies"
    }, 
    scoreThreshold: {
        name: "scoreThreshold",
        label: "Score Threshold",
        type: "number",
        default: 0.3,
        info: "Filter out scores below this threshold where score is the sum of the normalised metrics weighted as above"
    }
}