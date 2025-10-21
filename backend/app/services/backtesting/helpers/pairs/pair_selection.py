import networkx as nx

def select_pairs_max_weight(pairs, weight_key="score"):
    """
    Select pairs of stocks using maximum weight matching on a graph.

    Args:
        pairs (list): List of dicts representing candidate pairs, e.g.
                      [{"stock1": "AAPL", "stock2": "MSFT", "score": 0.9}, ...]
        weight_key (str): Key in the dict to use as edge weight in matching.

    Returns:
        list: Selected pairs (subset of input pairs) representing maximum weighted matching.
    """

    # Create an undirected graph
    G = nx.Graph()

    # Add edges to graph: nodes are stocks, edges are pairs, weighted by score
    for p in pairs:
        s1, s2, w = p["stock1"], p["stock2"], p[weight_key]
        # Store the original pair dict in edge data for easy retrieval
        G.add_edge(s1, s2, weight=w, data=p)

    # Compute maximum weight matching
    # maxcardinality=False means we only care about maximizing weight, not number of edges
    matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=False, weight="weight")

    # Extract the corresponding original pair dicts for the selected edges
    selected_pairs = []
    for u, v in matching:
        edge_data = G[u][v]["data"]
        selected_pairs.append(edge_data)

    return selected_pairs
