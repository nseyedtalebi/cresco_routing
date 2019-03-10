import networkx as nx
import numpy as np

from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.classes.graphviews import subgraph_view
from random import sample,randint
from collections import namedtuple
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

#def place_pipeline(num_stages,req_capacities,input_nodes,output_node,model):
def test_placements(print_placements=True):
    test_graph = nx.complete_graph(n=9)
    capacities = {node:0 for node in test_graph.nodes}
    capacities[4] = 10
    base = {'g':test_graph,'slow_edge':100,'fast_edge':1,'capacities':capacities}
    diagonal = {**base,'fast_edges':((0,4),(4,8))}
    shared = {**base,'fast_edges':((4,5),)}
    v_shaped = {**base,'fast_edges':((0,4),(2,4))}
    diag_p = get_placements(get_model(**diagonal)[0],terminals=(0,8),required_capacity=10)[0]
    shared_p = get_placements(get_model(**shared)[0],terminals=(4,5),required_capacity=10)[0]
    v_shaped_p = get_placements(get_model(**v_shaped)[0],terminals=(0,2),required_capacity=10)[0]
    if print_placements:
        for placement in (diag_p,shared_p,v_shaped_p,):
            print(f'{placement.node} {placement.weight} {placement.tree.edges}')
    assert diag_p.node == 4 and diag_p.weight == 2
    assert shared_p.node == 4 and shared_p.weight == 1
    assert v_shaped_p.node == 4 and v_shaped_p.weight == 2

def get_capacities_by_num_fast_edges(g,fast_edges):
    #To test try this:
    '''for info in sorted(capacities,key= lambda v:capacities[v]['fast_edge_count'],reverse=True):
    print(capacities[info])'''
    LOW = 1
    MED = 5
    HI = 10
    capacities = {node:{'fast_edge_count':0,'capacity':0} for node in g.nodes}
    for node in chain(*fast_edges):
        capacities[node]['fast_edge_count'] += 1
    ranked_edgecounts = list(sorted(fast_edge_counts,key=lambda v:fast_edge_counts[v],reverse=True))
    groupsize,extras = divmod(len(ranked_edgecounts),3)
    for node in ranked_edgecounts[0:groupsize]:
        capacities[node]['capacity'] = HI
    for node in ranked_edgecounts[groupsize:groupsize*2]:
        capacities[node]['capacity'] = MED
    for node in ranked_edgecounts[groupsize*2:]:
        capacities[node]['capacity'] = LOW
    return capacities

PipeStage = namedtuple('PipeStage',('input_nodes','reqd_capacity'))
'''
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

So what I need to do is:
-Write something that accepts a spec and returns a list of placements
-Modify stage placement function to accept function that will operate over terminals
so I can try both steiner tree and minimum spanning tree
-Modify get_model to handle randomized edge weights too
-write something to randomly decide which edges are fast edges based on a desired density of fast edges
-write anything that might help load and run simulations
-wrangle resulting data to finish results section

'''
'''graph_size=32
model_params = {'g':nx.complete_graph(n=graph_size),'slow_edge':100,'fast_edge':1}
model_params['fast_edges'] = sample(tuple(model_params['g'].edges),100)

model,weights,capacities = get_model(**model_params)
required_capacity = 3
placements = get_placements(model,set((2,6)),required_capacity)
'''
#after placing node, reduce capacity by required amount
