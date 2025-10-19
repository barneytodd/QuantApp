import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram


def correl_dist(corr: pd.DataFrame) -> pd.DataFrame:
    """Convert correlation matrix to distance matrix for clustering"""
    dist = np.sqrt(0.5 * (1 - corr))
    return dist

def get_cluster_var(cov: pd.DataFrame, cluster_items: list) -> float:
    """Compute variance of a cluster of assets"""
    sub_cov = cov.loc[cluster_items, cluster_items]
    w = 1 / np.diag(sub_cov)
    w /= w.sum()
    var = np.dot(w, np.dot(sub_cov, w))
    return var

def hrp_allocation(cov: pd.DataFrame) -> pd.Series:
    """
    Perform Hierarchical Risk Parity allocation
    cov: pd.DataFrame, covariance matrix with symbols as index and columns
    Returns: pd.Series of weights
    """
    # 1. Correlation matrix
    corr = cov.corr()
    
    # 2. Distance matrix
    dist = correl_dist(corr)
    
    # 3. Hierarchical clustering
    link = linkage(dist, method='single')
    
    # 4. Quasi-diagonalization
    dendro = dendrogram(link, no_plot=True)
    ordered_indices = dendro['leaves']
    ordered_assets = cov.columns[ordered_indices]
    
    # 5. Recursive bisection allocation
    weights = pd.Series(1.0, index=ordered_assets)
    clusters = [ordered_assets.tolist()]
    
    while clusters:
        cluster = clusters.pop(0)
        if len(cluster) <= 1:
            continue
        split = len(cluster) // 2
        cluster_1 = cluster[:split]
        cluster_2 = cluster[split:]
        
        var_1 = get_cluster_var(cov, cluster_1)
        var_2 = get_cluster_var(cov, cluster_2)
        alpha = 1 - var_1 / (var_1 + var_2)
        
        weights[cluster_1] *= alpha
        weights[cluster_2] *= 1 - alpha
        
        clusters.append(cluster_1)
        clusters.append(cluster_2)
    
    return weights / weights.sum()
