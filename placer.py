import networkx as nx
import numpy as np
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.algorithms.tree.mst import minimum_spanning_tree
from networkx.algorithms.operators.all import compose_all
from random import sample,randint,seed,uniform
from collections import namedtuple,Sequence
from itertools import chain
from math import floor

PlacementRecord = namedtuple('PlacementRecord',('node','weight','tree',))
#initialize rng for reproducibility
def get_placements(model,terminals,required_capacity,algorithm='steiner'):
    placements = []
    if algorithm not in ('steiner','mst'):
        raise ValueError("algorithm must be one of these: 'steiner','mst'")
    for v in model.nodes:
        if model.nodes[v]['capacity'] >= required_capacity:
            terminals_U_v = list(set(terminals).union([v]))
            if algorithm == 'steiner':
                tree = steiner_tree(model,terminals_U_v)
            if algorithm == 'mst':
                tree = minimum_spanning_tree(model.subgraph(terminals_U_v))
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

def get_model_random_edge_weights(g,lo,hi,capacities):
    for edge in g.edges:
        g.add_edge(*edge,weight=uniform(lo,hi))
    for node in g.nodes:
        g.nodes[node]['capacity']=capacities[node]
    weights = {}
    for i in range(len(g)):
        for j in range(len(g)):
            if i!=j:
                weights[i,j] = g.get_edge_data(i,j)['weight']
    #uniform distr capacities
    capacities = g.nodes.data()
    return g,weights,capacities

def place_stages_randomly(spec,model):
    placements = []
    for stage in reversed(spec):
        possible_placements = [node for node in model.nodes\
         if model.nodes[node]['capacity'] >= stage['reqd_capacity']]
        selected_node = sample(possible_placements,1)[0]
        tree = steiner_tree(model,
            list(set(stage['input_nodes']+[selected_node])))#terminals
        best_placement = PlacementRecord(selected_node,
            total_weight(tree),
            tree)
        placements.append(best_placement)
        model.nodes[best_placement.node]['capacity'] = 0
    tree = steiner_tree(model,[p.node for p in placements])
    trees = [tree]+[p.tree for p in placements]
    return list(reversed(placements)),compose_all(trees)

def place_stages_individually(spec,model,algorithm):
    placements = []
    #start from last stage
    for stage in reversed(spec):
        best_placement = get_placements(model,stage['input_nodes'],stage['reqd_capacity'],algorithm)[0]
        placements.append(best_placement)
        #Make sure this node isn't reused
        #In future versions, could reduce capacity by cost and allow multiple placements
        #on a single node
        model.nodes[best_placement.node]['capacity'] = 0
    tree = steiner_tree(model,[p.node for p in placements])
    trees = [tree]+[p.tree for p in placements]
    return list(reversed(placements)),compose_all(trees)

def place_stages_iteratively(spec,model,algorithm):
    placements = []
    #start from last stage
    r_spec = list(reversed(spec))
    for idx,stage in enumerate(r_spec):
        best_placement = get_placements(model,stage['input_nodes'],stage['reqd_capacity'],algorithm)[0]
        placements.append(best_placement)
        #Make sure this node isn't reused
        model.nodes[best_placement.node]['capacity'] = 0
        try:
            (r_spec[idx+1]['input_nodes']).append(best_placement.node)
        except IndexError as ex:
            pass#we've reached the last element
    trees = [p.tree for p in placements]
    return list(reversed(placements)),compose_all(trees)

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

def get_random_fast_edges(edges,pct_fast):
    if pct_fast < 0 or pct_fast > 1:
        raise ValueError('pct_fast should be a percentage between 0 and 1')
    num_fast = floor(len(edges)*pct_fast)
    return sample(edges,num_fast)

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
