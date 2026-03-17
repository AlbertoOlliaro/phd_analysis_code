import networkx as nx
import itertools

def kpp_neg(G, k):
    """
    KPP-NEG: Find k nodes whose removal maximally increases fragmentation.
    Uses a brute-force search for small graphs.
    """
    if k <= 0 or k > len(G):
        raise ValueError("k must be between 1 and number of nodes in the graph.")

    best_set = None
    best_fragmentation = -1

    for nodes in itertools.combinations(G.nodes(), k):
        H = G.copy()
        H.remove_nodes_from(nodes)
        # Fragmentation: 1 - (size of largest component / total nodes remaining)
        if len(H) == 0:
            frag = 1.0
        else:
            largest_cc = max(len(c) for c in nx.connected_components(H))
            frag = 1 - (largest_cc / len(G))
        if frag > best_fragmentation:
            best_fragmentation = frag
            best_set = nodes

    return best_set, best_fragmentation


def kpp_pos(G, k):
    """
    KPP-POS: Find k nodes that maximize reachability.
    Uses a greedy approach.
    """
    if k <= 0 or k > len(G):
        raise ValueError("k must be between 1 and number of nodes in the graph.")

    selected = set()
    for _ in range(k):
        best_node = None
        best_reach = -1
        for node in set(G.nodes()) - selected:
            reach_nodes = set()
            for s in selected | {node}:
                reach_nodes |= nx.single_source_shortest_path_length(G, s).keys()
            if len(reach_nodes) > best_reach:
                best_reach = len(reach_nodes)
                best_node = node
        selected.add(best_node)

    return selected, best_reach


if __name__ == "__main__":
    # Example graph
    G = nx.erdos_renyi_graph(8, 0.3, seed=42)

    # KPP-NEG: Disrupt network
    neg_nodes, frag_score = kpp_neg(G, k=2)
    print(f"KPP-NEG nodes: {neg_nodes}, fragmentation score: {frag_score:.3f}")

    # KPP-POS: Maximize reach
    pos_nodes, reach_score = kpp_pos(G, k=2)
    print(f"KPP-POS nodes: {pos_nodes}, reachability: {reach_score}")
