export const filters = {
    "Global": [
        {
            name: "maxBidAsk",
            label: "Max Average Bid-Ask Spread",
            type: "number",
            default: 0.02,
            info: "Maximum allowed average bid-ask spread measured by the proxy (high-low)/close"
        },
        {
            name: "maxDrawdown",
            label: "Max Drawdown",
            type: "number",
            default: 0.8,
            info: "Maximum allowed drawdown over the period in question"
        },
        {
            name: "skewness",
            label: "Lower Bound for Skew",
            type: "number",
            default: -0.2,
            info: "Minimum allowed value for skewness of results"
        },
        {
            name: "kurtosis",
            label: "Upper Bound for Kurtosis",
            type: "number",
            default: 10,
            info: "Maximum allowed value for Kurtosis"
        },
        {
            name: "maxVolatility",
            label: "Maximum Volatility (%)",
            type: "number",
            default: 80,
            info: "Maximum allowed volatility of any stock"
        }
    ],

    "Momentum": [
        {
            name: "percentageAboveMA",
            label: "Min frequency that close > MA (%)",
            type: "number",
            default: 70,
            info: "Minimum frequency that close > 200 day MA to be considered for momentum strategies"
        },
        {
            name: "avSlope",
            label: "Minimum Required Average MA Slope",
            type: "number",
            default: 0.015,
            info: "Minimum average slope of 200 day MA"
        },
        {
            name: "posReturns",
            label: "Min Percentage of Daily Returns > 0",
            type: "number",
            default: 55,
            info: "Minimum frequency that daily returns are positive"
        },
        {
            name: "minVolatilityMomentum",
            label: "Min Volatility (%)",
            type: "number",
            default: 10,
            info: "Minimum required volatility for momentum strategies"
        }
    ],

    "Mean-reversion": [
        {
            name: "autocorrelation",
            label: "Max Autocorrelation of Daily Returns",
            type: "number",
            default: 0,
            info: "Maximum lag-1 autocorrelation"
        },
        {
            name: "zscoreReversion",
            label: "Z-Score Reversal %",
            type: "number",
            default: 10,
            info: "Minimum required percentage of reversions after 5 days from crossing the reversion threshold"
        },
        {
            name: "zscoreThreshold",
            label: "Z-Score Threshold",
            type: "number",
            default: 2,
            info: "Number of standard deviations from the mean to set the reversion threshold for z-score reversion"
        }
    ],

    "Breakout": [
        {
            name: "minVolatilityBreakout",
            label: "Min Volatility (%)",
            type: "number",
            default: 15,
            info: "Minimum required volatility for breakout strategies"
        }
    ]
}