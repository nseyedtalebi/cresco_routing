import placer
import timeit
import pickle
from statistics import mean

placer.seed(1988)#Does this even matter?
repeat_num_times = 3
graph_size = 32

#fast_edge_pcts = [pct*0.01 for pct in range(5,100,5)]
fast_edge_pcts = [pct*0.01 for pct in range(10,100,10)]

iterations = 30

results_for_pct = {}
for fast_edge_pct in fast_edge_pcts:
    results = {'random':[],
                'individual_steiner':[],
                'iterative_steiner':[],
                'individual_mst':[],
                'iterative_mst':[]
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
            results[name].append(placer.total_weight(tree))
    results_for_pct[fast_edge_pct] = results
with open('performance_fast_edge_pct.pickled','wb') as pickleout:
    pickle.dump(results_for_pct,pickleout)




'''
things to check, all averaged over many different runs and for both approaches, MST:

-results for both approaches and MST with different densities of fast edges (lots,few, etc)
-results for both approaches and MST with randomized edge weights+capacities
-runtime and results for all with a few different pipeline depths
'''