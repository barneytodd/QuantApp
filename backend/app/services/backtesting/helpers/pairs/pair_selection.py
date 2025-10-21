import networkx as nx

def select_pairs_max_weight(pairs, weight_key="score"):
    """
    Select pairs using maximum weight matching.

    Args:
        pairs: list of dicts like
            [{"stock1": "AAPL", "stock2": "MSFT", "score": 0.9}, ...]
        weight_key: which key to use as the edge weight.

    Returns:
        list of selected pairs (subset of input pairs).
    """
    G = nx.Graph()

    # Add edges with weights
    for p in pairs:
        s1, s2, w = p["stock1"], p["stock2"], p[weight_key]
        G.add_edge(s1, s2, weight=w, data=p)

    # Solve maximum weight matching
    matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=False, weight="weight")

    # Extract the actual pair dicts
    selected_pairs = []
    for u, v in matching:
        edge_data = G[u][v]["data"]
        selected_pairs.append(edge_data)

    return selected_pairs
