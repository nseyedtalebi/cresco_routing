import networkx as nx
import numpy as np
import steiner_ilp

from networkx.algorithms.approximation.steinertree import steiner_tree
from random import sample

graph_size = 16
u = nx.complete_graph(n=graph_size)
slow_edge = 100
fast_edge=  1
num_fast = 2
num_terminals = 2
fast_edges = sample(tuple(u.edges),num_fast)
terminals = sample(list(u.nodes()),num_terminals)
ccap_low = 1 
ccap_hi = 10
for edge in u.edges:
    u.add_edge(*edge,weight= fast_edge if edge in fast_edges else slow_edge)
weights = {}
for i in range(len(u)):
    for j in range(len(u)):
        if i!=j:
            weights[i,j] = u.get_edge_data(i,j)['weight']

#st = steiner_tree(u,terminals)
sv,se,mdl = steiner_ilp.bidirected_steiner_tree(set(u.nodes),set(u.edges),terminals,weights)
#
"""TODO
-Finish implementing something that solves the pipeline placement problem
-Implement something to find theoretical optimum for each stage
--for each stage, we can reduce number of inputs to check for optimum because we
can exclude based on capacity and whether or not that stages has been assigned

Experiments:
-compare theoretical optimum to heuristic, then heuristic to NetworkX steiner
    -objective performance and speed on realistic hierarcy
    -obj performance and speed on random graph
        -vary number of levels of link speeds
        -vary graph size
        -vary prob distribution for fast edges
        -vary prob dist for compute capacity
        
"""
    


