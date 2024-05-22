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

    # Function L(x, y)
    def L(x, y):
        if x == y:
            return 1
        elif x < y:
            return -sum_M(x, y)
        return 0
    
    # Sum of M(x, y) for all x < y
    def sum_M(x, y):
        sum_m = 0
        for i in range(x):
            for j in range(i + 1, x):
                sum_m += M_values.get((i, j), 0)
        return sum_m
    
    # Calculate M for all subgraphs
    def calculate_M_values(G):
        M_values = {}
        for k in range(len(G.edges) + 1):
            for subset in combinations(G.edges, k):
                subgraph = nx.Graph(subset)
                num_components = nx.number_connected_components(subgraph)
                M_values[subset] = n ** num_components
        return M_values
    
    # Calculate M(G)
    M_values = calculate_M_values(G)
    M_sum = 0
    for subset in combinations(G.edges, len(G.edges)):
        subgraph = nx.Graph(subset)
        num_components = nx.number_connected_components(subgraph)
        M_sum += L(len(subset), len(G.edges)) * (n ** num_components)
    
    return M_sum

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
        # If G has no edges, the chromatic polynomial is x^n
        return [0] * G.number_of_nodes() + [1]
    else:
        # Choose an arbitrary edge
        u, v = next(iter(G.edges()))  # Convert EdgeView to iterator

        # Construct G' by deleting the edge
        G_prime = G.copy()
        G_prime.remove_edge(u, v)

        # Construct G'' by contracting the edge
        G_double_prime = nx.contracted_edge(G, (u, v), self_loops=False)

        # Recursively calculate the coefficients of the chromatic polynomials of G' and G''
        coeffs_prime = chromatic_polynomial_coefficients(G_prime)
        coeffs_double_prime = chromatic_polynomial_coefficients(G_double_prime)

        # The coefficients of the chromatic polynomial of G are the difference of the coefficients of the chromatic polynomials of G' and G''
        return [c_prime - c_double_prime for c_prime, c_double_prime in zip_longest(coeffs_prime, coeffs_double_prime, fillvalue=0)]
    
def chromatic_polynomial_formula(G):
    
    H = generate_flat_subgraphs(G)
    
    coefficients = {}
    
    for h in H:
        key = nx.number_connected_components(h)
        coefficients[key] = coefficients.get(key, 0) + mobius(h)
        
    coefficients[nx.number_connected_components(G)] += mobius(G)
    
    return coefficients

def write_formula(coefficients):
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
                formula += "^" + str(key)
    return formula