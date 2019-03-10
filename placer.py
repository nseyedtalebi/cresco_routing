import networkx as nx
import numpy as np
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.classes.graphviews import subgraph_view
from random import sample,randint
from collections import namedtuple,Sequence
from itertools import chain

PlacementRecord = namedtuple('PlacementRecord',('node','weight','tree',))

def get_placements(model,terminals,required_capacity):
    placements = []
    for v in model.nodes:
        if model.nodes[v]['capacity'] >= required_capacity:
            tree = steiner_tree(model,list(set(terminals).union([v])))
            cur_weight = total_weight(tree)
            placements.append(PlacementRecord(v,cur_weight,tree))
    ranked = sorted(placements,key=lambda p:p.weight)
    return ranked

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

def place_stages_individually(spec,model):
    placements = []
    #start from last stage
    for stage in reversed(spec):
        best_placement = get_placements(model,stage['input_nodes'],stage['reqd_capacity'])[0]
        placements.append(best_placement)
        #Make sure this node isn't reused
        model.nodes[best_placement.node]['capacity'] = 0
    return list(reversed(placements))

def place_stages_iteratively(spec,model):
    placements = []
    #start from last stage
    r_spec = list(reversed(spec))
    for idx,stage in enumerate(r_spec):
        best_placement = get_placements(model,stage['input_nodes'],stage['reqd_capacity'])[0]
        placements.append(best_placement)
        #Make sure this node isn't reused
        model.nodes[best_placement.node]['capacity'] = 0
        try:
            (r_spec[idx+1]['input_nodes']).append(best_placement.node)
        except IndexError as ex:
            pass#we've reached the last element
    return list(reversed(placements)),list(reversed(r_spec))

def get_random_pipe_spec(nodes,depth,num_inputs,req_capacities,add_output_node=True):
    spec = []
    if not isinstance(num_inputs,Sequence):
        per = num_inputs
        num_inputs = [per for i in range(0,depth)]
    if not isinstance(req_capacities,Sequence):
        per = req_capacities
        req_capacities = [per for i in range(0,depth)]
    if add_output_node:
        num_inputs[-1] += 1
    for i in range(0,depth):
        spec.append({'input_nodes':sample(nodes,num_inputs[i]),
            'reqd_capacity':req_capacities[i]})
    return spec

'''
arb =  {'input_nodes':sample(nodes,num_inputs[i]),
            'reqd_capacity':req_capacities[i]}
        print(arb)
        spec += arb
The get_capacities_by_num_fast_edges function I wrote is probably not helpful.
Adapt it to set capacities randomly: high (few), med (some), low (lots)

greedy approach:starting from last stage, find optimal placement for each stage using previous stage's
placement as input

other approach: find optimum for each stage individually, then find steiner tree linking placements
and output

things to check, all averaged over many different runs and for both approaches, MST:
-run time for graphs of different sizes for both methods and MST (do this first)
 do the following with largest feasible graph
 **for results, try both approaches, MST, and random placement**
-results for both approaches and MST with different densities of fast edges (lots,few, etc)
-results for both approaches and MST with randomized edge weights
-runtime and results for all with a few different pipeline depths

So what I need to do is:
-Write something that accepts a spec and returns a list of placements
!!mostly done

-Modify stage placement function to accept function that will operate over terminals
so I can try steiner tree and minimum spanning tree
!!this may not be worth it, mst and steiner take different args I think

-Modify get_model to handle randomized edge weights too
-write something to randomly decide which edges are fast edges based on a desired density of fast edges
-write anything that might help load and run simulations
-wrangle resulting data to finish results section
-write something to do random placements without breaking capacity requirements


graph_size=32
model_params = {'g':nx.complete_graph(n=graph_size),'slow_edge':100,'fast_edge':1}
model_params['fast_edges'] = sample(tuple(model_params['g'].edges),100)
model_params['capacities'] = {node:100 for node in model_params['g'].nodes}
model,weights,capacities = get_model(**model_params)
spec = get_random_pipe_spec(model.nodes,2,3,1)

required_capacity = 3
placements = get_placements(model,set((2,6)),required_capacity)
'''
#after placing node, reduce capacity by required amount
