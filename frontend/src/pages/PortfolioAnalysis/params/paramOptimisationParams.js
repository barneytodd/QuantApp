export const params = {
    sharpe: {
        name: "sharpe",
        label: "Sharpe Ratio",
        type: "number",
        default: 0.4,
        group: "scoringParams",
        info: "Set weighting for sharpe ratio in the combined metric used to optimise parameters"
    },
    cagr: {
        name: "cagr",
        label: "CAGR",
        type: "number",
        default: 0.3,
        group: "scoringParams",
        info: "Set weighting for compound annual growth rate in the combined metric used to optimise parameters"
    },
    maxDrawdown: {
        name: "max_drawdown",
        label: "Max Drawdown",
        type: "number",
        default: 0.2,
        group: "scoringParams",
        info: "Set weighting for max drawdown in the combined metric used to optimise parameters"
    },
    winRate: {
        name: "win_rate",
        label: "Win Rate",
        type: "number",
        default: 0.1,
        group: "scoringParams",
        info: "Set weighting for trade win rate in the combined metric used to optimise parameters"
    },
    numTrials: {
        name: "iterations",
        label: "Number of Trials",
        type: "number",
        default: 50,
        group: "optimParams",
        info: "Number of optimisation trials for each strategy"
    },
    windowLength: {
        name: "window_length",
        label: "Window Length",
        type: "number",
        default: 3,
        group: "optimParams",
        info: "Window length in years for walkforward backtest"
    }
}