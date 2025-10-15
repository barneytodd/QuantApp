export const optimisationParams = [
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
        default: 50
    }
]