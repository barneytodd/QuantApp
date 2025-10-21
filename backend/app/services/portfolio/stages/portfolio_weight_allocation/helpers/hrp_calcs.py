import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage

# === Hierarchical Risk Parity (HRP) Allocation Engine ===

def correl_dist(corr: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a correlation matrix to a distance matrix suitable for clustering.

    Args:
        corr: pd.DataFrame, correlation matrix

    Returns:
        pd.DataFrame, distance matrix
    """
    dist = np.sqrt(0.5 * (1 - corr))
    return dist


def get_cluster_var(cov: pd.DataFrame, cluster_items: list) -> float:
    """
    Compute the variance of a cluster of assets using inverse-variance weighting.

    Args:
        cov: pd.DataFrame, covariance matrix
        cluster_items: list of asset names in the cluster

    Returns:
        float, cluster variance
    """
    sub_cov = cov.loc[cluster_items, cluster_items]
    w = 1 / np.diag(sub_cov)         # inverse-variance weights
    w /= w.sum()                     # normalize weights
    var = np.dot(w, np.dot(sub_cov, w))
    return var


def hrp_allocation(cov: pd.DataFrame) -> pd.Series:
    """
    Perform Hierarchical Risk Parity (HRP) allocation.

    Steps:
        1. Compute correlation matrix
        2. Convert to distance matrix
        3. Perform hierarchical clustering
        4. Quasi-diagonalize assets based on dendrogram
        5. Allocate weights recursively via bisection

    Args:
        cov: pd.DataFrame, covariance matrix with symbols as index and columns

    Returns:
        pd.Series of normalized HRP weights
    """
    # --- 1. Correlation matrix ---
    corr = cov.corr()
    
    # --- 2. Distance matrix for clustering ---
    dist = correl_dist(corr)
    
    # --- 3. Hierarchical clustering using linkage ---
    link = linkage(dist, method='single')
    
    # --- 4. Quasi-diagonalization via dendrogram ---
    dendro = dendrogram(link, no_plot=True)
    ordered_indices = dendro['leaves']
    ordered_assets = cov.columns[ordered_indices]
    
    # --- 5. Recursive bisection allocation ---
    weights = pd.Series(1.0, index=ordered_assets)
    clusters = [ordered_assets.tolist()]
    
    while clusters:
        cluster = clusters.pop(0)
        if len(cluster) <= 1:
            continue
        
        # Split cluster into two halves
        split = len(cluster) // 2
        cluster_1 = cluster[:split]
        cluster_2 = cluster[split:]
        
        # Compute cluster variances
        var_1 = get_cluster_var(cov, cluster_1)
        var_2 = get_cluster_var(cov, cluster_2)
        
        # Allocate weights proportionally to inverse risk
        alpha = 1 - var_1 / (var_1 + var_2)
        weights[cluster_1] *= alpha
        weights[cluster_2] *= 1 - alpha
        
        # Recurse on sub-clusters
        clusters.append(cluster_1)
        clusters.append(cluster_2)
    
    # --- Normalize weights to sum to 1 ---
    return weights / weights.sum()
