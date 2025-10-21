def compute_pair_score(corr, pval, beta=None, w_corr=0.5, w_coint=0.5):
    """
    Compute a composite score for a pair of stocks, balancing correlation and cointegration.

    Args:
        corr (float): Pearson correlation coefficient between the two stocks (-1 to 1).
        pval (float): P-value from cointegration test (0 to 1). Lower is better.
        beta (float, optional): Hedge ratio slope from regression. Extreme values may be penalized.
        w_corr (float): Weight for correlation in composite score (0-1).
        w_coint (float): Weight for cointegration in composite score (0-1).

    Returns:
        float: Composite pair score; higher values indicate better pairs.
    """

    # --- Correlation score ---
    # Absolute correlation: closer to 1 indicates stronger linear relationship
    corr_score = abs(corr)

    # --- Cointegration score ---
    # Smaller p-value indicates stronger cointegration
    coint_score = 1 - pval

    # --- Optional beta penalty ---
    # Penalize hedge ratios that are too extreme (too small or too large)
    beta_penalty = 1.0
    if beta is not None and (beta < 0.2 or beta > 5):
        beta_penalty = 0.5

    # --- Weighted composite score ---
    score = (w_corr * corr_score + w_coint * coint_score) * beta_penalty
    return score
