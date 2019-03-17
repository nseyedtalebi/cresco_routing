import placer
import timeit
import functools

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

graph_sizes = [8,16,32]
for size in graph_sizes:
    uniform_model_params = placer.get_default_model_params(size,1)
    model,weights,capacities = placer.get_model(**uniform_model_params)
    spec = [{'input_nodes':[0,1,2],'reqd_capacity':1}]
    to_run = prepare_functions(spec,model)
    trees = {name:func()[1] for name,func in to_run.items()}
    weights = {key:placer.total_weight(val) for key,val in trees.items()}
    print(weights)
    '''rnd_p,rnd_tree = placer.place_stages_randomly(spec,model)
    ind_p,ind_tree = placer.place_stages_individually(spec,model,'steiner')
    ind_mst_p,ind_mst_tree = placer.place_stages_individually(spec,model,'mst')
    it_p,it_tree = placer.place_stages_iteratively(spec,model,'steiner')
    it_mst_p,it_mst_tree = placer.place_stages_iteratively(spec,model,'mst')
    trees = {'random':rnd_tree,
    'individual':ind_tree,
    'iterative':it_tree,
    'individual_mst':ind_mst_tree,
    'iterative_mst':it_mst_tree}
    weights = {key:placer.total_weight(val) for key,val in trees.items()}
    print(weights)'''


'''
things to check, all averaged over many different runs and for both approaches, MST:
-run time for graphs of different sizes for both methods and MST (do this first)
 do the following with largest feasible graph
 **for results, try both approaches, MST, and random placement**
-results for both approaches and MST with different densities of fast edges (lots,few, etc)
-results for both approaches and MST with randomized edge weights+capacities
-runtime and results for all with a few different pipeline depths
'''