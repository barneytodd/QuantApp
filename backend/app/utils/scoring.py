def compute_pair_score(corr, pval, beta=None, w_corr=0.5, w_coint=0.5):
    """
    Composite score balancing correlation & cointegration.

    Args:
        corr: correlation coefficient (-1..1)
        pval: cointegration test p-value (0..1)
        beta: optional hedge ratio slope
        w_corr: correlation weight
        w_coint: cointegration weight

    Returns:
        score (float)
    """
    corr_score = abs(corr)        # closer to 1 is better
    coint_score = 1 - pval        # smaller p-value is better

    beta_penalty = 1.0
    if beta is not None and (beta < 0.2 or beta > 5):
        beta_penalty = 0.5  # penalize extreme hedge ratios

    return (w_corr * corr_score + w_coint * coint_score) * beta_penalty
