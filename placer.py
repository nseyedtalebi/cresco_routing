import functools
from networkx.algorithms.approximation.steinertree import metric_closure
from networkx.algorithms.tree.mst import minimum_spanning_tree
from networkx.algorithms.operators.all import compose_all
from networkx.utils import pairwise
from random import sample,randint,seed,uniform
from collections import namedtuple,Sequence
from itertools import chain,product,filterfalse
from math import floor

import networkx as nx
import numpy as np

PlacementRecord = namedtuple('PlacementRecord',('node','weight','tree',))
#initialize rng for reproducibility
def get_placements(model,terminals,capacities,required_capacity,algorithm='steiner'):
    placements = []
    if algorithm not in ('steiner','mst'):
        raise ValueError("algorithm must be one of these: 'steiner','mst'")
    if algorithm == 'steiner':
        M = metric_closure(model)
    for v in model.nodes:
        if capacities[v] >= required_capacity:
            terminals_U_v = list(set(terminals).union([v]))
            if algorithm == 'steiner':
                tree = steiner_tree_from_metric_closure(model, M, terminals_U_v)
            if algorithm == 'mst':
                tree = minimum_spanning_tree(model.subgraph(terminals_U_v))
            cur_weight = total_weight(tree)
            placements.append(PlacementRecord(v, cur_weight, tree))
    ranked = sorted(placements,key=lambda p:p.weight)
    return ranked

def total_weight(graph):
    return sum((graph.edges[edge]['weight'] for edge in graph.edges))

def get_capacity_dict(g):
    return {node:d['capacity'] for node,d in dict(g.nodes.data()).items()}

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
    capacities = get_capacity_dict(g)
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
    capacities = get_capacity_dict(g)
    return g,weights,capacities

def place_stages_randomly(spec,model):
    placements = []
    capacities = get_capacity_dict(model)
    for stage in reversed(spec):
        possible_placements = [node for node in model.nodes\
         if capacities[node] >= stage['reqd_capacity']]
        selected_node = sample(possible_placements,1)[0]
        tree = minimum_spanning_tree(model.subgraph(stage['input_nodes']+[selected_node]))
        best_placement = PlacementRecord(selected_node,
            total_weight(tree),
            tree)
        placements.append(best_placement)
        capacities[best_placement.node] = 0
    trees = [p.tree for p in placements]
    return list(reversed(placements)),compose_all(trees)

def place_stages_individually(spec,model,algorithm):
    placements = []
    capacities = get_capacity_dict(model)
    #start from last stage
    for stage in reversed(spec):
        best_placement = get_placements(model,stage['input_nodes'],
            capacities,stage['reqd_capacity'],algorithm)[0]
        placements.append(best_placement)
        #Make sure this node isn't reused
        #In future versions, could reduce capacity by cost and allow multiple placements
        #on a single node
        capacities[best_placement.node] = 0
    M = metric_closure(model)
    tree = steiner_tree_from_metric_closure(model, M, 
                                           [p.node for p in placements])
    trees = [tree]+[p.tree for p in placements]
    return list(reversed(placements)),compose_all(trees)

def place_stages_iteratively(spec,model,algorithm):
    placements = []
    capacities = get_capacity_dict(model)
    #start from last stage
    r_spec = list(reversed(spec))
    for idx,stage in enumerate(r_spec):
        try:
            inputs = stage['input_nodes']+[placements[idx-1].node]
        except IndexError as ex:
            inputs = stage['input_nodes']
        best_placement = get_placements(model, inputs, capacities,
                                        stage['reqd_capacity'], algorithm)[0]
        placements.append(best_placement)
        #Make sure this node isn't reused
        capacities[best_placement.node] = 0
    trees = [p.tree for p in placements]
    return list(reversed(placements)),compose_all(trees)

def get_random_pipe_spec(nodes,depth,num_inputs,req_capacities,add_output_node=True):
    if not isinstance(num_inputs,Sequence):
        per = num_inputs
        num_inputs = [per for i in range(0,depth)]
    if not isinstance(req_capacities,Sequence):
        per = req_capacities
        req_capacities = [per for i in range(0,depth)]
    if add_output_node:
        num_inputs[-1] += 1
    return tuple({'input_nodes':sample(nodes,num_inputs[i]),
            'reqd_capacity':req_capacities[i]} for i in range(0,depth))
    '''for i in range(0,depth):
        spec.append({'input_nodes':sample(nodes,num_inputs[i]),
            'reqd_capacity':req_capacities[i]})
    return spec'''

def get_random_fast_edges(edges,pct_fast):
    if pct_fast < 0 or pct_fast > 1:
        raise ValueError('pct_fast should be a percentage between 0 and 1')
    num_fast = floor(len(edges)*pct_fast)
    return sample(edges,num_fast)

def get_default_model_params(graph_size,fast_edge_pct):
    g = nx.complete_graph(n=graph_size)
    model_params = {'g':g,'slow_edge':10,'fast_edge':1}
    model_params['fast_edges'] = get_random_fast_edges(g.edges,fast_edge_pct)
    model_params['capacities'] = {node:1 for node in g.nodes}
    return model_params

def prepare_functions(spec,model):
    return {'random':functools.partial(place_stages_randomly,spec,model),
    'individual':functools.partial(place_stages_individually,spec,model,
        'steiner'),
    'iterative':functools.partial(place_stages_iteratively,spec,model,
        'steiner'),
    'individual_mst':functools.partial(place_stages_individually,spec,
        model,'mst'),
    'iterative_mst':functools.partial(place_stages_iteratively,spec,
        model,'mst')
    }

def steiner_tree_from_metric_closure(G, M, terminal_nodes, weight='weight'):
    """ Return an approximation to the minimum Steiner tree of a graph given its
    metric closure

    Parameters
    ----------
    G : NetworkX graph
    H : Metric closure of G as computed by metric_closure() from the Steiner
        tree module
    terminal_nodes : list
         A list of terminal nodes for which minimum steiner tree is
         to be found.

    Returns
    -------
    NetworkX graph
        Approximation to the minimum steiner tree of `G` induced by
        `terminal_nodes` .

    Notes
    -----
    This function is a slightly modified version of the steiner tree function in
    networkx.algorithms.approximation.steinertree.steiner_tree. It takes both G
    and its metric closure as input. This is useful in situations where we want
    to find Steiner trees for different sets of terminals in the same graph.
    """
    # Use the 'distance' attribute of each edge provided by the metric closure
    # graph.
    H = M.subgraph(terminal_nodes)
    mst_edges = nx.minimum_spanning_edges(H, weight='distance', data=True)
    # Create an iterator over each edge in each shortest path; repeats are okay
    edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)
    T = G.edge_subgraph(edges)
    return T