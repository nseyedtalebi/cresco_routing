import networkx as nx
import numpy as np
import steiner_ilp
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.classes.graphviews import subgraph_view
from random import sample,randint
from collections import OrderedDict

def find_optimal_stage(V,E,T,weights,capacities,required):
    models = {}
    for v in V:
        if capacities[v] >= required:
            sv,se,models[v] = steiner_ilp.bidirected_steiner_tree(set(V),set(E),set(T).union(set((v,))),weights=weights)
    return models[min(models,key=lambda m:float(models[m].getAttr('objval')))],models

def opt_stage(model,terminals,required_capacity):
    trees = {}
    for v in model.nodes:
        if model.nodes[v]['capacity'] >= required_capacity:
            trees[v] = steiner_tree(model,terminals)
    #return OrderedDict(sorted(trees.items(),key=lambda t:(total_weight(t[1]))))
    return trees

def total_weight(graph):
    return sum((graph.edges[edge]['weight'] for edge in graph.edges))
    
def get_model(graph_size,slow_edge,fast_edge,num_fast,num_terminals,ccap_low,
ccap_hi):
    u = nx.complete_graph(n=graph_size)
    fast_edges = sample(tuple(u.edges),num_fast)
    for edge in u.edges:
        u.add_edge(*edge,weight=fast_edge if edge in fast_edges else slow_edge)
    for node in u.nodes:
        u.nodes[node]['capacity']=randint(ccap_low,ccap_hi)
    weights = {}
    for i in range(len(u)):
        for j in range(len(u)):
            if i!=j:
                weights[i,j] = u.get_edge_data(i,j)['weight']
    #uniform distr capacities
    capacities = u.nodes.data()
    return u,weights,capacities;


#best_model,models = find_optimal_stage(u.nodes,u.edges,set((2,6)),weights,capacities,required_capacity)
#graph_size = 32 ran out of memory
model_params = {'graph_size':32,'slow_edge':100,'fast_edge':1,'num_fast':10,
    'num_terminals':2,'ccap_low':1,'ccap_hi':10}
model,weights,capacities = get_model(**model_params)
required_capacity = 3
trees = opt_stage(model,set((2,6)),required_capacity)

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
    


