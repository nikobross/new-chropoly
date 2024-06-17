import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations, zip_longest

def are_edges_adjacent(edge1, edge2):
    # Unpack the nodes from the edges
    edge1_node1, edge1_node2 = edge1
    edge2_node1, edge2_node2 = edge2

    # Check if the edges share a node
    if edge1_node1 in edge2 or edge1_node2 in edge2:
        return True
    else:
        return False

def generate_subgraphs(G):
    edges = list(G.edges())
    nodes = list(G.nodes())
    subgraphs = []

    for r in range(len(edges) + 1):
        # Generate all combinations of edges of length r
        for edge_combination in combinations(edges, r):
            # Create a new graph with the selected edges
            subgraph = nx.Graph()
            subgraph.add_nodes_from(nodes)  # Add all nodes to the subgraph
            subgraph.add_edges_from(edge_combination)
            subgraphs.append(subgraph)

    return subgraphs

def calculate_rank(graph):
    # Number of vertices
    num_vertices = graph.number_of_nodes()
    
    # Number of connected components
    num_connected_components = nx.number_connected_components(graph)
    
    # Rank of the graph
    rank = num_vertices - num_connected_components
    
    return rank

def is_flat(subgraph, G):
    
    # Calculate the rank of H
    rank_G = calculate_rank(G)
    
    other_edges = set(G.edges()) - set(subgraph.edges())

    # Filter other_edges to only include edges adjacent to at least one edge in the subgraph
    other_edges = [edge for edge in other_edges if any(are_edges_adjacent(edge, sub_edge) for sub_edge in subgraph.edges())]
    
    # Check if adding any edge from G \ H increases the rank of H
    for edge in G.edges():
        if edge not in subgraph.edges():
            subgraph.add_edge(*edge)
            new_rank_H = calculate_rank(subgraph)
            subgraph.remove_edge(*edge)
            if new_rank_H > rank_G:
                return False
    
    if nx.is_isomorphic(subgraph, G):
        return False
    
    return True

def generate_flat_subgraphs(G):
    subgraphs = generate_subgraphs(G)
    flats = []
    for subgraph in subgraphs:
        if is_flat(subgraph, G):
            flats.append(subgraph)
    return flats

def mobius(G):
    
    phi = nx.Graph()
    phi.add_nodes_from(G.nodes())
    
    if nx.is_isomorphic(G, phi):
        return 1
    
    return -sum(mobius(h) for h in generate_flat_subgraphs(G))

def chromatic_polynomial(G, colors):
    
    H = generate_flat_subgraphs(G)
    
    total = sum(mobius(h) * colors ** nx.number_connected_components(h) for h in H)
    total += colors ** nx.number_connected_components(G)
    
    return total

def chromatic_polynomial_coefficients(G):
    if G.number_of_edges() == 0:
        return {G.number_of_nodes(): 1}
    else:
        u, v = next(iter(G.edges()))

        G_prime = G.copy()
        G_prime.remove_edge(u, v)

        G_double_prime = nx.contracted_edge(G, (u, v), self_loops=False)

        coeffs_prime = chromatic_polynomial_coefficients(G_prime)
        coeffs_double_prime = chromatic_polynomial_coefficients(G_double_prime)

        coefficients = {}
        for key in coeffs_prime:
            coefficients[key] = coeffs_prime[key]
        for key in coeffs_double_prime:
            if key in coefficients:
                coefficients[key] -= coeffs_double_prime[key]
            else:
                coefficients[key] = -coeffs_double_prime[key]
        
        return coefficients
    
def chromatic_polynomial_formula(G):
    
    H = generate_flat_subgraphs(G)
    
    coefficients = {}
    
    for h in H:
        key = nx.number_connected_components(h)
        coefficients[key] = coefficients.get(key, 0) + mobius(h)
        
    coefficients[nx.number_connected_components(G)] += mobius(G)
    
    return coefficients

def write_formula(coefficients):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    formula = ""
    for key in sorted(coefficients.keys(), reverse=True):
        if coefficients[key] == 0:
            continue
        if coefficients[key] > 0 and formula:
            formula += " + "
        elif coefficients[key] < 0:
            formula += " - "
        if abs(coefficients[key]) != 1 or key == 0:
            formula += str(abs(coefficients[key]))
        if key > 0:
            formula += "n"
            if key > 1:
                formula += str(key).translate(superscripts)
    return formula