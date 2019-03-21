import placer
import timeit
import functools
import pickle
from statistics import mean
placer.seed(1988)
def prepare_functions(spec,model):
    return {'random':functools.partial(placer.place_stages_randomly,spec,model),
    'individual':functools.partial(placer.place_stages_individually,spec,model,
        'steiner'),
    'iterative':functools.partial(placer.place_stages_iteratively,spec,model,
        'steiner'),
    'individual_mst':functools.partial(placer.place_stages_individually,spec,
        model,'mst'),
    'iterative_mst':functools.partial(placer.place_stages_iteratively,spec,
        model,'mst')
    }

graph_sizes = range(3,15)#40
#[8,16,32,64,128]
results = {}
for size in graph_sizes:
    uniform_model_params = placer.get_default_model_params(size,1)
    model,weights,capacities = placer.get_model(**uniform_model_params)
    spec = [{'input_nodes':[0,1,2],'reqd_capacity':1}]
    to_run = prepare_functions(spec,model)
    times = {name:mean(timeit.repeat(func,number=1,repeat=5)) for name,func in to_run.items()}
    #print(times)
    results[size] = times
with open('runtimes.pickled','wb') as pickled:
    pickle.dump(results,pickled)

'''
TODO:
-Add something to this file to pickle the results
-Write something to process results and produce graphs
-If graphs look ok with smaller runs, do a full-sized run
-write similar code for pipe depth instead of graph size (reuse as much as possible)

things to check, all averaged over many different runs and for both approaches, MST:
-run time for graphs of different sizes for both methods and MST (do this first)
 do the following with largest feasible graph
 **for results, try both approaches, MST, and random placement**
-results for both approaches and MST with different densities of fast edges (lots,few, etc)
-results for both approaches and MST with randomized edge weights+capacities
-runtime and results for all with a few different pipeline depths
'''