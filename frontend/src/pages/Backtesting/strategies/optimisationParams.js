export const optimisationParams = [
    {
        name: "minCvFolds",
        label: "Required number of folds for cross-validation",
        type: "number",
        default: 5,
    },
    {
        name: "maxCvFolds",
        label: "Max number of folds for cross-validation",
        type: "number",
        default: 10,
    }, 
    {
        name: "foldLength",
        label: "Years of data in each fold",
        type: "number",
        default: 2
    },
    { 
        name: "iterations",
        label: "No of iterations for Bayesian optimisation",
        type: "integer",
        default: 40
    }
]