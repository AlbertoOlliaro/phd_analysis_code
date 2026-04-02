import networkx as nx
import itertools
import matplotlib.pyplot as plt


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

    # https://networkx.org/documentation/stable/reference/functions.html
    # run the functions from the above link instead of passing by Gephi

    print("-------------------- BORGATTI GRAPH WITH COUNTRIES ----------------------")
    filepath = 'C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/analysis/1.5_edges_verbose.csv'
    G = nx.read_adjlist(filepath, comments='#', delimiter=',', create_using=None, nodetype=str, encoding='utf-8')

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    nx.draw_networkx(G, ax=ax, with_labels=True, node_color='blue', edge_color='black', font_size=10)
    plt.show()

    for k in range(1, 10):
        print(f"-------------------- k = {k} ----------------------")
        # KPP-NEG: Disrupt network
        neg_nodes, frag_score = kpp_neg(G, k=k)
        print(f"KPP-NEG nodes: {neg_nodes}, fragmentation score: {frag_score:.3f}")
        # KPP-POS: Maximize reach
        pos_nodes, reach_score = kpp_pos(G, k=k)
        print(f"KPP-POS nodes: {pos_nodes}, reachability: {reach_score}")



    print("-------------------- BORGATTI GRAPH WITH REGIONS ----------------------")
    filepath = 'C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/analysis/1.7_subregions_edges_only.csv'
    G = nx.read_adjlist(filepath, comments='#', delimiter=',', create_using=None, nodetype=str, encoding='utf-8')

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    nx.draw_networkx(G, ax=ax, with_labels=True, node_color='blue', edge_color='black', font_size=10)
    plt.show()

    for k in range(1, 10):
        print(f"-------------------- k = {k} ----------------------")
        # KPP-NEG: Disrupt network
        neg_nodes, frag_score = kpp_neg(G, k=k)
        print(f"KPP-NEG nodes: {neg_nodes}, fragmentation score: {frag_score:.3f}")
        # KPP-POS: Maximize reach
        pos_nodes, reach_score = kpp_pos(G, k=k)
        print(f"KPP-POS nodes: {pos_nodes}, reachability: {reach_score}")
