from random import sample
import unittest
import pdb
import itertools

import networkx as nx
from networkx.algorithms.tree.mst import minimum_spanning_tree
import networkx.algorithms.isomorphism as iso

import placer

def get_model_and_spec_for_test():
    graph_size = 16
    g = nx.complete_graph(n=graph_size)
    spec = placer.get_random_pipe_spec(g.nodes, 
                                        2,#depth 
                                        3,#3,#num inputs per stage
                                        1,#reqd capacity per stage
                                        True)#add output node
    terminals = [node for stage in spec for node in stage['input_nodes']]
    #add two extra nodes for where we want the placements
    placements = []
    fast_edges = []
    for stage in spec:
        inputs = stage['input_nodes']
        possible_placements = [node for node in g.nodes if node not in inputs and node not in placements]
        placement = sample(possible_placements,1)[0]
        placements.append(placement)
        fast_edges += list(itertools.product([placement],inputs))
    fast_edges += [(placements[0],placements[1])]
    capacities = {node:1 if node in placements else 0 for node in g.nodes}
    model_params = {'g':g, 'slow_edge':10, 'fast_edge':1, 
                    'fast_edges':fast_edges, 'capacities': capacities}
    return placer.get_model(**model_params)[0], spec, placements, g.edge_subgraph(fast_edges)

def get_forced_example():
    graph_size = 9
    g = nx.complete_graph(n=graph_size)
    spec = (placer.PipeStage([0,1,2],1),placer.PipeStage([4,5,6,7],1))
    terminals = [node for stage in spec for node in stage['input_nodes']]
    #add two extra nodes for where we want the placements
    placements = [2,8]
    fast_edges = []
    fast_edges += list(itertools.product([2],spec[0].input_nodes))
    fast_edges += list(itertools.product([8],spec[1].input_nodes))
    fast_edges += [(2,8)]
    capacities = {node:1 if node in placements else 0 for node in g.nodes}
    model_params = {'g':g, 'slow_edge':10, 'fast_edge':1, 
                    'fast_edges':fast_edges, 'capacities': capacities}
    return placer.get_model(**model_params)[0], spec, placements, g.edge_subgraph(fast_edges)

model,spec,pl,tgt = get_forced_example()
p,t = placer.place_stages(spec,model,'mst',iterative=True)
p2,t2 = placer.place_stages(spec,model,'steiner',iterative=True)
print(nx.is_isomorphic(t,tgt))
print(nx.is_isomorphic(t2,tgt))
#pdb.set_trace()
'''class TestPlacer(unittest.TestCase):

    def setUp(self):
        self.model, self.spec, self.placements, self.target_tree =\
        get_model_and_spec_for_test()

    def test_placers(self):
        print(self.model)
        print(self.spec)
        print(self.placements)
        print(self.target_tree)
        to_test = placer.prepare_functions(self.spec,self.model)
        for method,func in to_test.items():
            if method != 'random':
                with self.subTest(method=method):
                    #if 'mst' in method:
                    #    pdb.set_trace()
                    test_placements,test_tree = func()
                    print(method)
                    print(self.target_tree.edges)
                    print(test_tree.edges)
                    print(set(test_tree.edges).difference(set((self.target_tree.edges))))
                    print(nx.is_isomorphic(self.target_tree,test_tree))
                    print('Fast edges:')
                    for u,v,data in self.model.edges.data():
                        if data['weight'] == 1:
                            print(u,v)
                    print('Capacities')
                    for node,cap in self.model.nodes.data():
                        if cap['capacity'] > 0:
                            print(node)
                    self.assertTrue(nx.is_isomorphic(self.target_tree,test_tree))

if __name__ == '__main__':
    unittest.main()'''
