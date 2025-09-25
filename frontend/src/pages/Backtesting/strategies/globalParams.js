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
    optimise: false
  },
  {
    name: "endDate",
    label: "End Date",
    type: "date",
    default: formatDate(today),
    category: "advanced",
    optimise: false
  },
  {
    name: "initialCapital",
    label: "Initial Capital ($)",
    type: "number",
    default: 10000,
    category: "advanced",
    optimise: false,
    integer: true
  },
  {
    name: "slippage",
    label: "Slippage (%)",
    type: "number",
    default: 0.05, 
    category: "advanced",
    optimise: false,
    integer: false
  },
  {
    name: "transactionCostPct",
    label: "Transaction Cost (%)",
    type: "number",
    default: 0.01, 
    category: "advanced",
    optimise: false,
    integer: false
  },
  {
    name: "fixedTransactionCost",
    label: "Fixed Transaction Cost",
    type: "number",
    default: 0, 
    category: "advanced",
    optimise: false,
    integer: true
  },
  {
    name: "rebalanceFrequency",
    label: "Rebalance Frequency (days)",
    type: "number",
    default: null, 
    category: "advanced",
    optimise: false,
    integer: true
  },
  {
    name: "stopLoss",
    label: "Stop Loss (%)",
    type: "number",
    default: null,
    category: "advanced",
    optimise: false,
    integer: false
  },
  {
    name: "takeProfit",
    label: "Take Profit (%)",
    type: "number",
    default: null,
    category: "advanced",
    optimise: false,
    integer: false
  },
];
