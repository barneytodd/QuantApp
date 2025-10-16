def composite_score(aggregated_results, scoring_params, weights=None):
    metrics_list = [
        {
            "sharpe": r["avgSharpe"], 
            "cagr": r["avgCAGR"], 
            "max_drawdown": r["avgMaxDrawdown"], 
            "win_rate": r["avgWinRate"]
        } 
        for r in aggregated_results
    ]

    if len(metrics_list) == 0:
        return []

    weights = weights or [1.0 / len(metrics_list)] * len(metrics_list)
    
    scores = []
    for w, metrics in zip(weights, metrics_list):
        sharpe = metrics["sharpe"] / 3
        cagr = metrics["cagr"] / 50
        max_dd = 1 - (metrics["max_drawdown"] / 50)
        win_rate = metrics["win_rate"] / 100
        score = (
            scoring_params["sharpe"] * sharpe 
            + scoring_params["cagr"] * cagr 
            + scoring_params["max_drawdown"] * max_dd 
            + scoring_params["win_rate"] * win_rate
        )
        scores.append(score * w)

    return sum(scores)
