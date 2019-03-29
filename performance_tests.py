import timeit
import pickle
import argparse
from statistics import mean
from random import sample
from math import fsum,floor

import networkx as nx

import placer

placer.seed(1988)#Does this even matter?

def run_fast_edge_tests():
    graph_size = 32
    #fast_edge_pcts = [pct*0.01 for pct in range(5,100,5)]
    fast_edge_pcts = [pct*0.01 for pct in range(2,100,2)]
    iterations = 40

    results_for_pct = {}
    for fast_edge_pct in fast_edge_pcts:
        results = {'random':[],
                    'individual_steiner':[],
                    'iterative_steiner':[],
                    'individual_mst':[],
                    'iterative_mst':[],
                    'est_lower_bound':[]
                }
        for iteration in range(0,iterations):
            print(f'{fast_edge_pct*100} % fast edges, iteration {iteration}')
            model_params = placer.get_default_model_params(graph_size,fast_edge_pct)
            model,weights,capacities = placer.get_model(**model_params)
            spec = placer.get_random_pipe_spec(model.nodes,8,#depth
                                                     3,#num inputs per stage
                                                     1)#reqd capacity per stage
            to_run = placer.prepare_functions(spec,model)
            for name,func in to_run.items():
                placements,tree = func()
                if name == 'individual_steiner':
                    composed = nx.compose_all((p.tree for p in placements))
                    results['est_lower_bound'] += [placer.total_weight(composed)]
                results[name].append(placer.total_weight(tree))
        results_for_pct[fast_edge_pct] = results
    with open('performance_fast_edge_pct.pickled','wb') as pickleout:
        pickle.dump(results_for_pct,pickleout)

def run_capacity_effect_test():
    graph_size = 32
    capacity_pcts = [pct*0.01 for pct in range(2,100,2)]
    iterations = 40

    results_for_pct = {}
    for capacity_pct in capacity_pcts:
        results = {'random':[],
                    'individual_steiner':[],
                    'iterative_steiner':[],
                    'individual_mst':[],
                    'iterative_mst':[],
                    'est_lower_bound':[]
                }
        for iteration in range(0,iterations):
            print(f'{capacity_pct*100} % nodes with sufficent capacity, iteration {iteration}')
            model_params = placer.get_default_model_params(graph_size,0.05)
            model,weights,capacities = placer.get_model(**model_params)
            picked = sample(tuple((node for node in model.nodes)),
                            floor(capacity_pct*len(model.nodes)))
            for node,data in model.nodes.data():
                if node in picked:
                    data['capacity'] = 2

            spec = placer.get_random_pipe_spec(model.nodes,8,#depth
                                                     3,#num inputs per stage
                                                     2)#reqd capacity per stage
            to_run = placer.prepare_functions(spec,model)
            for name,func in to_run.items():
                placements,tree = func()
                if name == 'individual_steiner':
                    composed = nx.compose_all((p.tree for p in placements))
                    results['est_lower_bound'] += [placer.total_weight(composed)]
                results[name].append(placer.total_weight(tree))
        results_for_pct[capacity_pct] = results
    with open('performance_capacity_pct.pickled','wb') as pickleout:
        pickle.dump(results_for_pct,pickleout)

def run_inputs_per_stage_tests():
    graph_size = 96
    inputs_per_stage = [i for i in range(1,11)]
    iterations = 40

    results_for_pct = {}
    for num_inputs in inputs_per_stage:
        results = {'random':[],
                    'individual_steiner':[],
                    'iterative_steiner':[],
                    'individual_mst':[],
                    'iterative_mst':[],
                    'est_lower_bound':[]
                }
        for iteration in range(0,iterations):
            print(f'{num_inputs} inputs per stage, iteration {iteration}')
            model_params = placer.get_default_model_params(graph_size,0.05)
            model,weights,capacities = placer.get_model(**model_params)
            spec = placer.get_random_pipe_spec(model.nodes,8,#depth
                                                     num_inputs,#num inputs per stage
                                                     1)#reqd capacity per stage
            to_run = placer.prepare_functions(spec,model)
            for name,func in to_run.items():
                placements,tree = func()
                if name == 'individual_steiner':
                    composed = nx.compose_all((p.tree for p in placements))
                    results['est_lower_bound'] += [placer.total_weight(composed)]
                results[name].append(placer.total_weight(tree))
        results_for_pct[num_inputs] = results
    with open('performance_inputs_per_stage.pickled','wb') as pickleout:
        pickle.dump(results_for_pct,pickleout)

def run_pipe_depth_tests():
    graph_size = 64
    iterations = 40
    results_for_depth = {}
    for depth in range(1,20):
        results = {'random':[],
                    'individual_steiner':[],
                    'iterative_steiner':[],
                    'individual_mst':[],
                    'iterative_mst':[],
                    'est_lower_bound':[]
                }
        for iteration in range(0,iterations):
            print(f'{depth} pipe depth, iteration {iteration}')
            #choose fast edge pct based on point of max separation between
            #steiner and mst methods
            model_params = placer.get_default_model_params(graph_size,0.05)
            model,weights,capacities = placer.get_model(**model_params)
            spec = placer.get_random_pipe_spec(model.nodes,depth,#depth
                                                     3,#num inputs per stage
                                                     1)#reqd capacity per stage
            to_run = placer.prepare_functions(spec,model)
            for name,func in to_run.items():
                placements,tree = func()
                results[name].append(placer.total_weight(tree))
                if name == 'individual_steiner':
                    composed = nx.compose_all((p.tree for p in placements))
                    results['est_lower_bound'] += [placer.total_weight(composed)]
        results_for_depth[depth] = results
    print(results_for_depth)
    with open('performance_pipe_depth.pickled','wb') as pickleout:
        pickle.dump(results_for_depth,pickleout)

def run_randomized_model_tests():
    graph_size = 32
    iterations = 40
    pipe_depth = 8
    results_for_sigma = {}
    for sigma in (i*0.1 for i in range(10,50,1)):
        results = {'random':[],
                    'individual_steiner':[],
                    'iterative_steiner':[],
                    'individual_mst':[],
                    'iterative_mst':[],
                    'est_lower_bound':[]
                }
        for iteration in range(0,iterations):
            print(f'Sigma:{sigma}, iteration {iteration}')       
            model = placer.get_randomized_model(graph_size,10,sigma)
            spec = placer.get_random_pipe_spec(model.nodes,pipe_depth,#depth
                                                     3,#num inputs per stage
                                                     1)#reqd capacity per stage
            to_run = placer.prepare_functions(spec,model)
            for name,func in to_run.items():
                placements,tree = func()
                results[name].append(placer.total_weight(tree))
                if name == 'individual_steiner':
                    composed = nx.compose_all((p.tree for p in placements))
                    results['est_lower_bound'] += [placer.total_weight(composed)]
        results_for_sigma[sigma] = results

    print(results_for_sigma)
    with open('performance_randomized_sigma.pickled','wb') as pickleout:
        pickle.dump(results_for_sigma,pickleout)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run tests to get simulation results for placer.py")
    parser.add_argument('test',help='The name of the test to run. One of either "randomized", "pipe-depth" or "fast-edges"')
    args = parser.parse_args()
    if args.test == 'randomized':
        run_randomized_model_tests()
    if args.test == 'pipe-depth':
        run_pipe_depth_tests()
    if args.test == 'fast-edges':
        run_fast_edge_tests()
    if args.test == 'capacity':
        run_capacity_effect_test()
    if args.test == 'inputs-per':
        run_inputs_per_stage_tests()