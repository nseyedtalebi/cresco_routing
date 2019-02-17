import networkx as nx
import numpy as np
import steiner_ilp
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.classes.graphviews import subgraph_view
from random import sample,randint
from collections import namedtuple

PlacementRecord = namedtuple('PlacementRecord',('node','weight','tree'))
def find_optimal_stage(V,E,T,weights,capacities,required):
    models = {}
    for v in V:
        if capacities[v] >= required:
            sv,se,models[v] = steiner_ilp.bidirected_steiner_tree(set(V),set(E),set(T).union(set((v,))),weights=weights)
    return models[min(models,key=lambda m:float(models[m].getAttr('objval')))],models

def place_stage(model,terminals,required_capacity):
    placements = []
    for v in model.nodes:
        if model.nodes[v]['capacity'] >= required_capacity:
            tree = steiner_tree(model,list(set(terminals).union([v])))
            cur_weight = total_weight(tree)
            placements.append(PlacementRecord(v,cur_weight,tree))
    ranked = sorted(placements,key=lambda p:p.weight)
    return ranked[0]

def total_weight(graph):
    return sum((graph.edges[edge]['weight'] for edge in graph.edges))
    
def get_model(g,slow_edge,fast_edge,fast_edges,capacities):
    fast_edges += tuple(tuple(reversed(edge)) for edge in fast_edges)
    for edge in g.edges:
        if (edge in fast_edges) or (reversed(edge) in fast_edges):
            g.add_edge(*edge,weight=fast_edge)
        else:
            g.add_edge(*edge,weight=slow_edge)
    for node in g.nodes:
        g.nodes[node]['capacity']=capacities[node]
        #randint(ccap_low,ccap_hi)
    weights = {}
    for i in range(len(g)):
        for j in range(len(g)):
            if i!=j:
                weights[i,j] = g.get_edge_data(i,j)['weight']
    #uniform distr capacities
    capacities = g.nodes.data()
    return g,weights,capacities

#def place_pipeline(num_stages,req_capacities,input_nodes,output_node,model):
def test_placements(print_placements=True):
    test_graph = nx.complete_graph(n=9)
    capacities = {node:0 for node in test_graph.nodes}
    capacities[4] = 10
    base = {'g':test_graph,'slow_edge':100,'fast_edge':1,'capacities':capacities}
    diagonal = {**base,'fast_edges':((0,4),(4,8))}
    shared = {**base,'fast_edges':((4,5),)}
    v_shaped = {**base,'fast_edges':((0,4),(2,4))}
    diag_p = place_stage(get_model(**diagonal)[0],terminals=(0,8),required_capacity=10)
    shared_p = place_stage(get_model(**shared)[0],terminals=(4,5),required_capacity=10)
    v_shaped_p = place_stage(get_model(**v_shaped)[0],terminals=(0,2),required_capacity=10)
    if print_placements:
        for placement in (diag_p,shared_p,v_shaped_p,):
            print(f'{placement.node} {placement.weight} {placement.tree.edges}')
    assert diag_p.node == 4 and diag_p.weight == 2
    assert shared_p.node == 4 and shared_p.weight == 1
    assert v_shaped_p.node == 4 and v_shaped_p.weight == 2

#best_model,models = find_optimal_stage(g.nodes,g.edges,set((2,6)),weights,capacities,required_capacity)
#graph_size = 32 ran out of memory

#graph_size=32
#model_params = {'g':nx.complete_graph(n=graph_size),'slow_edge':100,'fast_edge':1,'ccap_low':1,'ccap_hi':10}
#model_params['fast_edges'] = sample(tuple(model_params['g'].edges),100)
#model,weights,capacities = get_model(**model_params)
#required_capacity = 3
#placement = place_stage(model,set((2,6)),required_capacity)

#after placing node, set capacity to zero to prevent it from being used in next iteration

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
    


