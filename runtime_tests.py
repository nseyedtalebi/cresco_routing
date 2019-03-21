import placer
import timeit
import pickle
from statistics import mean

placer.seed(1988)#Does this even matter?
repeat_num_times = 3
def test_runtimes_vs_graph_size(max_size):
    graph_sizes = range(3,max_size)
    #[8,16,32,64,128]
    graph_size_runtimes = {}
    for size in graph_sizes:
        uniform_model_params = placer.get_default_model_params(size,1)
        model,weights,capacities = placer.get_model(**uniform_model_params)
        spec = [{'input_nodes':[0,1,2],'reqd_capacity':1}]
        to_run = placer.prepare_functions(spec,model)
        times = {name:mean(timeit.repeat(func,number=1,repeat=repeat_num_times)) for name,func in to_run.items()}
        print('\n'+str(times)+'\n')
        graph_size_runtimes[size] = times
    return graph_size_runtimes

def test_runtimes_vs_pipe_depth(graph_size,max_depth):
    if graph_size < max_depth:
        print('Graph is smaller than max pipe depth, so some nodes will be used for the input to multiple stages')
    pipe_depths = range(1,max_depth)
    pipe_depth_runtimes = {}
    for depth in pipe_depths:
        print(depth)
        uniform_model_params = placer.get_default_model_params(graph_size,1)
        model,weights,capacities = placer.get_model(**uniform_model_params)
        spec = placer.get_random_pipe_spec(model.nodes,
            depth,
            1,
            1,
            add_output_node=True)
        to_run = placer.prepare_functions(spec,model)
        times = {name:mean(timeit.repeat(func,number=1,repeat=repeat_num_times)) for name,func in to_run.items()}
        print('\n'+str(times)+'\n')
        pipe_depth_runtimes[depth] = times
    return pipe_depth_runtimes

'''graph_size_runtimes = test_runtimes_vs_graph_size(32)
with open('graph_size_runtimes.pickled','wb') as pickled:
   pickle.dump(graph_size_runtimes,pickled)'''

pipe_depth_runtimes = test_runtimes_vs_pipe_depth(16,15)
print(pipe_depth_runtimes)
with open('pipe_depth_runtimes.pickled','wb') as pickled:
    pickle.dump(pipe_depth_runtimes,pickled)

'''
TODO:
-If graphs look ok with smaller runs, do a full-sized run
!!do later
-write similar code for pipe depth instead of graph size (reuse as much as possible)

things to check, all averaged over many different runs and for both approaches, MST:
-run time for graphs of different sizes for both methods and MST (do this first)
 do the following with largest feasible graph
 **for results, try both approaches, MST, and random placement**
-results for both approaches and MST with different densities of fast edges (lots,few, etc)
-results for both approaches and MST with randomized edge weights+capacities
-runtime and results for all with a few different pipeline depths
'''