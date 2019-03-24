import functools
from dataclasses import dataclass
import typing
from networkx.algorithms.approximation.steinertree import metric_closure
from networkx.algorithms.tree.mst import minimum_spanning_tree
from networkx.algorithms.operators.all import compose_all
from networkx.utils import pairwise
from random import sample,randint,seed,uniform
from collections import namedtuple,Sequence
from itertools import chain,product,filterfalse
from math import floor
import pdb
import networkx as nx
import numpy as np

PlacementRecord = namedtuple('PlacementRecord',('node','weight','tree',))

#initialize rng for reproducibility
def get_placements(model,terminals,capacities,required_capacity,
    model_metric_closure=None):
    placements = []
    for v in model.nodes:
        if capacities[v] >= required_capacity:
            terminals_U_v = list(set(terminals).union([v]))
            if model_metric_closure:
                tree = steiner_tree_from_metric_closure(model, model_metric_closure, terminals_U_v)
            else:
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

def place_stages(spec,model,algorithm,iterative=True):
    if algorithm == 'steiner' or not iterative:
        M = metric_closure(model)
    placements = []
    capacities = get_capacity_dict(model)
    #start from last stage
    r_spec = tuple(reversed(spec))
    for idx,stage in enumerate(r_spec):
        inputs = stage['input_nodes']
        if iterative:
            try:
                inputs += (placements[idx-1].node,)
            except IndexError as ex:
                pass#first stage
        if algorithm =='steiner':
            best_placement = get_placements(model, inputs,
                capacities,stage['reqd_capacity'], model_metric_closure=M)[0]
        if algorithm == 'mst':
            best_placement = get_placements(model, inputs,
                capacities,stage['reqd_capacity'])[0]
        if algorithm not in ('steiner','mst'):
            raise ValueError('Algorithm must be one of (steiner,mst)')
        placements.append(best_placement)
        #Make sure this node isn't reused
        #In future versions, could reduce capacity by cost and allow multiple placements
        #on a single node
        capacities[best_placement.node] = 0
    trees = [p.tree for p in placements]
    if not iterative:#tie the placed nodes together
        trees += [steiner_tree_from_metric_closure(model, M, 
                                           [p.node for p in placements])]
    return tuple(reversed(placements)),compose_all(trees)

def get_random_pipe_spec(nodes,depth,num_inputs,req_capacities,add_output_node=True):
    if not isinstance(num_inputs,Sequence):
        per = num_inputs
        num_inputs = [per for i in range(0,depth)]
    if not isinstance(req_capacities,Sequence):
        per = req_capacities
        req_capacities = [per for i in range(0,depth)]
    if add_output_node:
        num_inputs[-1] += 1
    stages = []
    picked = []
    for i in range(0,depth):
        eligible_nodes = [node for node in nodes if node not in picked]
        stage_inputs = sample(eligible_nodes,num_inputs[i])
        picked += stage_inputs
        stages.append(PipeStage(stage_inputs,1))
    return tuple(stages)
    '''return tuple({'input_nodes':sample(nodes,num_inputs[i]),
            'reqd_capacity':req_capacities[i]} for i in range(0,depth))'''
    '''for i in range(0,depth):
        spec.append({'input_nodes':sample(nodes,num_inputs[i]),
            'reqd_capacity':req_capacities[i]})
    return spec'''

@dataclass(frozen=True)
class PipeStage:
    input_nodes:'typing.Tuple'
    reqd_capacity:'int'

    def __init__(self,input_nodes,reqd_capacity)   :
        object.__setattr__(self,'input_nodes',tuple(input_nodes))
        object.__setattr__(self,'reqd_capacity',reqd_capacity)

    def __getitem__(self,key):
        return self.__dict__[key]

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
    'individual_steiner':functools.partial(place_stages,spec,model,'steiner',
                                    iterative=False),
    'iterative_steiner':functools.partial(place_stages,spec,model,'steiner',
                                    iterative=True),
    'individual_mst':functools.partial(place_stages,spec,model,'mst',
                                    iterative=False),
    'iterative_mst':functools.partial(place_stages,spec,model,'mst',
                                    iterative=True)
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

'''def get_model_and_test_spec():
    #inputs for stage 1: 0,1,4
    #stage 1 to be placed at 5
    #inputs for stage 2: 6,7,11,15
    #stage 2 to be placed at 10
    #5 and 10 should have capacity > 0, others all 0
    graph_size=16
    model_params = {'g':nx.complete_graph(n=graph_size),'slow_edge':100,'fast_edge':1}
    model_params['fast_edges'] = [
    (0,5),(1,5),(4,5),#three edges for inputs
    (5,10),#one edge to link stages
    (10,6),(10,7),(10,11),#three edges for inputs
    (10,15)#to the output node
    ]
    model_params['capacities'] = {node:1 for node in model_params['g'].nodes}
    model_params['capacities'][5] = 1
    model_params['capacities'][10] = 1
    model,weights,capacities = get_model(**model_params)
    pipe_spec = [{'input_nodes':[0,1,4],'reqd_capacity':1},#first stage
    {'input_nodes':[6,7,11,15],'reqd_capacity':1}#second stage
    ]
    #return placer.total_weight(model_params['g'])
    return model,pipe_spec

model,pipe_spec = get_model_and_test_spec()
#pdb.set_trace()
model,spec = get_model_and_test_spec()
it_placements,it_tree = place_stages(spec,model,'mst',iterative=False)
print(it_placements)
print(sorted(it_tree.edges))
print(total_weight(it_tree))
model,spec = get_model_and_test_spec()
ind_placements,ind_tree = place_stages(spec,model,'steiner',iterative=False)
print(ind_placements)
print(sorted(ind_tree.edges))
print(total_weight(ind_tree))'''
