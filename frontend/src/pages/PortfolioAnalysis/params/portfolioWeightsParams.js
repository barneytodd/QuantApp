export const params = {
    ewmaDecay: {
        name: "ewma_decay",
        label: "Exponential Decay for Expected Returns",
        type: "number",
        default: 0.94,
        group: "inputs",
        info: "Exponential decay value for calculating expected returns from walkforward returns"
    },
    riskAversion: {
        name: "risk_aversion",
        label: "Risk Aversion",
        type: "number",
        default: 0.5,
        group: "optimisation",
        info: "Penalises portfolio variance"
    },
    baselineReg: {
        name: "baseline_reg",
        label: "Baseline Regulation",
        type: "number",
        default: 0.1,
        group: "optimisation",
        info: "Penalises deviation from baseline hrp weights"
    },
    maxWeight: {
        name: "max_weight",
        label: "Max Weight",
        type: "number",
        default: 0.1,
        group: "optimisation",
        info: "Maximum allocation to a single asset"
    },
    minWeight: {
        name: "min_weight",
        label: "Min Weight",
        type: "number",
        default: 0,
        group: "optimisation",
        info: "Minimum allocation to a single asset"
    }
}