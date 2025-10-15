def composite_score(aggregated_results, weights=None):
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
        score = (0.5 * sharpe + 0.3 * cagr + 0.3 * max_dd + 0.1 * win_rate)
        scores.append(score * w)

    return sum(scores)
