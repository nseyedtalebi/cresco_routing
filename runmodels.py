import networkx as nx
from networkx.algorithms.approximation.steinertree import steiner_tree
from random import sample
from steiner_ilp import bidirected_steiner_tree

graph_size = 4
u = nx.complete_graph(n=graph_size)
slow_edge = 100
fast_edge=  1
num_fast = 2
num_terminals = 2
fast_edges = sample(tuple(u.edges),num_fast)
terminals = sample(list(u.nodes()),num_terminals)
for edge in u.edges:
    u.add_edge(*edge,weight= fast_edge if edge in fast_edges else slow_edge)
weights = {}
for i in range(len(u)):
    for j in range(len(u)):
        if i!=j:
            weights[i,j] = u.get_edge_data(i,j)['weight']

st = steiner_tree(u,terminals)
sv,se,mdl = bidirected_steiner_tree(set(u.nodes),set(u.edges),terminals,weights)
