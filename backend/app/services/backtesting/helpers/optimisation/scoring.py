def composite_score(aggregated_results, scoring_params, weights=None):
    """
    Compute a single composite score for a strategy or portfolio based on multiple metrics.

    Args:
        aggregated_results (list): List of aggregated results per symbol/strategy, 
                                   each containing metrics like avgSharpe, avgCAGR, etc.
        scoring_params (dict): Weights for each metric in the final score, e.g.
                               {"sharpe": 0.4, "cagr": 0.3, "max_drawdown": 0.2, "win_rate": 0.1}
        weights (list, optional): Optional weights for each symbol/strategy. Defaults to equal weights.

    Returns:
        float: Composite score combining Sharpe, CAGR, Max Drawdown, and Win Rate.
    """

    # --- Extract relevant metrics for each aggregated result ---
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
        # No results to score
        return 0  # returning 0 instead of empty list for consistency

    # --- Assign weights per symbol/strategy if not provided ---
    weights = weights or [1.0 / len(metrics_list)] * len(metrics_list)

    scores = []
    for w, metrics in zip(weights, metrics_list):
        # --- Normalize each metric to a comparable scale ---
        sharpe = metrics["sharpe"] / 3           # assume target Sharpe ~3
        cagr = metrics["cagr"] / 50              # assume target CAGR ~50%
        max_dd = 1 - (metrics["max_drawdown"] / 50)  # lower drawdown increases score
        win_rate = metrics["win_rate"] / 100     # convert % to 0-1

        # --- Weighted sum of metrics based on scoring_params ---
        score = (
            scoring_params.get("sharpe", 0) * sharpe 
            + scoring_params.get("cagr", 0) * cagr 
            + scoring_params.get("max_drawdown", 0) * max_dd 
            + scoring_params.get("win_rate", 0) * win_rate
        )

        # --- Apply overall weight for this symbol/strategy ---
        scores.append(score * w)

    # --- Sum weighted scores to get final composite score ---
    return sum(scores)
