// Utility to format dates as YYYY-MM-DD
const formatDate = (date) => date.toISOString().split("T")[0];

// Today's date
const today = new Date();

// One year ago
const oneYearAgo = new Date();
oneYearAgo.setFullYear(today.getFullYear() - 1);

// Global parameters apply to ALL strategies
// These define backtest-wide configuration and risk settings
export const globalParams = [
  {
    name: "startDate",
    label: "Start Date",
    type: "date",
    default: formatDate(oneYearAgo),
    category: "advanced",
    optimise: false,
    integer: false,
    group: "Date Range",
    info: "Date from which to begin trading \nRequired: date dd/mm/yyyy"
  },
  {
    name: "endDate",
    label: "End Date",
    type: "date",
    default: formatDate(today),
    category: "advanced",
    optimise: false,
    integer: false,
    group: "Date Range",
    info: "Date on which to finish trading and close all positions \nRequired: date dd/mm/yyyy"
  },
  {
    name: "initialCapital",
    label: "Initial Capital ($)",
    type: "number",
    default: 10000,
    category: "advanced",
    optimise: false,
    integer: true,
    group: "Capital & Risk Management",
    info: "Total initial capital for the portfolio"
  },
  {
    name: "slippage",
    label: "Slippage (%)",
    type: "number",
    default: 0.05, 
    category: "advanced",
    optimise: false,
    integer: false,
    group: "Trading Costs",
    info: "Percentage to estimate price slippage during each trade"
  },
  {
    name: "transactionCostPct",
    label: "Transaction Cost (%)",
    type: "number",
    default: 0.01, 
    category: "advanced",
    optimise: false,
    integer: false,
    group: "Trading Costs",
    info: "Percentage commission for each trade"
  },
  {
    name: "fixedTransactionCost",
    label: "Fixed Transaction Cost",
    type: "number",
    default: 0, 
    category: "advanced",
    optimise: false,
    integer: true,
    group: "Trading Costs",
    info: "Fixed commission for each trade"
  },
  {
    name: "stopLoss",
    label: "Stop Loss (%)",
    type: "number",
    default: null,
    category: "advanced",
    optimise: false,
    integer: false,
    group: "Capital & Risk Management",
    info: "Trade is closed if its percentage loss exceeds this bound"
  },
  {
    name: "takeProfit",
    label: "Take Profit (%)",
    type: "number",
    default: null,
    category: "advanced",
    optimise: false,
    integer: false,
    group: "Capital & Risk Management",
    info: "Trade is closed if its percentage profit exceeds this bound"
  },
  { 
    name: "positionSizing", 
    label: "Position Sizing (%)", 
    type: "number", 
    default: 100, 
    bounds: [1, 100], 
    category: "advanced", 
    optimise: true, 
    integer: false,
    group: "Capital & Risk Management",
    info: "Percentage of available capital allocated to each trade" 
  },
  { 
    name: "maxConcurrentPositions", 
    label: "Max Concurrent Positions", 
    type: "categorical", 
    default: "unlimited", 
    options: [1, 2, 3, 5, 10, 20, "unlimited"], 
    category: "advanced", 
    optimise: true,
    integer: true, 
    group: "Capital & Risk Management",
    info: "Maximum number of positions allowed to be open at any one time \nRequired: int \nSuggested values [1, 2, 3, 5, 10, 20, unlimited]"
  },
  { 
    name: "minHoldingPeriod", 
    label: "Minimum Holding Period", 
    type: "categorical", 
    default: 0, 
    options: [0, 1, 5, 10, 20, 60], 
    category: "advanced", 
    optimise: true,
    integer: true,
    group: "Capital & Risk Management",
    info: "Minimum number of days to stay open before closing any given position \nRequired: int \nSuggested values [0, 1, 5, 10, 20, 60]" 
  }
];
