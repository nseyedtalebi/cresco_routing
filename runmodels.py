import networkx as nx
import numpy as np
import steiner_ilp
from networkx.algorithms.approximation.steinertree import steiner_tree
from random import sample,randint
from collections import OrderedDict

def find_optimal_stage(V,E,T,weights,capacities,required):
    models = {}
    for v in V:
        if capacities[v] >= required:
            sv,se,models[v] = steiner_ilp.bidirected_steiner_tree(set(V),set(E),set(T).union(set((v,))),weights=weights)
    return models[min(models,key=lambda m:float(models[m].getAttr('objval')))],models

def opt_stage(V,E,T,weights,capacities,required):
    trees = {}
    for v in V:
        if capacities[v] >= required:
            g = nx.Graph()
            g.add_nodes_from(V)
            for e in E:
                g.add_edge(*e,weight=weights[e])
            trees[v] = steiner_tree(g,T)
    return OrderedDict(sorted(trees.items(),key=lambda t:total_weight(t[1].edges,\
    weights)))

def total_weight(E,weights):
    return sum((weights[e] for e in E))
#graph_size = 32 ran out of memory
graph_size=128
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

#sv,se,mdl = steiner_ilp.bidirected_steiner_tree(set(u.nodes),set(u.edges),terminals,weights)

#uniform distr capacities
capacities = {v:randint(ccap_low,ccap_hi) for v in u.nodes}
required_capacity = 3
trees = opt_stage(u.nodes,u.edges,set((2,6)),weights,capacities,required_capacity)
#best_model,models = find_optimal_stage(u.nodes,u.edges,set((2,6)),weights,capacities,required_capacity)
 

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
    


