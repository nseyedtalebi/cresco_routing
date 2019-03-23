from random import sample

import networkx as nx
from networkx.algorithms.tree.mst import minimum_spanning_tree
import networkx.algorithms.isomorphism as iso

import placer

def get_model_and_spec_for_test():
    graph_size = 16
    g = nx.complete_graph(n=graph_size)
    spec = placer.get_random_pipe_spec(g.nodes, 
                                        2,#depth 
                                        3,#num inputs per stage
                                        1,#reqd capacity per stage
                                        True)#add output node
    terminals = [node for stage in spec for node in stage['input_nodes']]
    #add two extra nodes for where we want the placements
    placements = sample([node for node in g.nodes if node not in terminals],2)
    target_tree = minimum_spanning_tree(g.subgraph(terminals+placements))
    fast_edges = list(target_tree.edges)
    capacities = {node:1 if node in placements else 0 for node in g.nodes}
    model_params = {'g':g, 'slow_edge':10, 'fast_edge':1, 
                    'fast_edges':fast_edges, 'capacities': capacities}
    return placer.get_model(**model_params)[0], spec, placements, target_tree

def get_model_and_test_spec():
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
    model,weights,capacities = placer.get_model(**model_params)
    pipe_spec = [{'input_nodes':[0,1,4],'reqd_capacity':1},#first stage
    {'input_nodes':[6,7,11,15],'reqd_capacity':1}#second stage
    ]
    #return placer.total_weight(model_params['g'])
    return model,pipe_spec

def compare_placements(one,other):
    one_nodes = [p.node for p in one]
    other_nodes = [p.node for p in other]
    return one_nodes == other_nodes

model, spec, placements, target_tree = get_model_and_spec_for_test()
it_placements,it_tree = placer.place_stages_iteratively(spec,model,'steiner')
print(nx.is_isomorphic(target_tree,it_tree))
print('done')
'''uniform_model_params = placer.get_default_model_params(8,1)
model,weights,capacities = placer.get_model(**uniform_model_params)

model,spec = get_model_and_test_spec()
it_placements,it_tree = placer.place_stages_iteratively(spec,model,'mst')
print(it_placements)
print(sorted(it_tree.edges))
print(placer.total_weight(it_tree))

model,spec = get_model_and_test_spec()
ind_placements,ind_tree = placer.place_stages_individually(spec,model,'mst')
print(ind_placements)
print(sorted(ind_tree.edges))
print(placer.total_weight(ind_tree))

model,spec = get_model_and_test_spec()
rnd_placements,rnd_tree = placer.place_stages_randomly(spec,model)
print(rnd_placements)
print(sorted(rnd_tree.edges))
print(placer.total_weight(rnd_tree))'''