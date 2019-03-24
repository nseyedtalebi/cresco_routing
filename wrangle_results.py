import pickle

import numpy as np
import matplotlib.pyplot as plt

import placer

#We don't actually want the functions, just the names
method_names = [name for name in placer.prepare_functions(None,None).keys()]
#*************************Graph Size********************************************
'''with open('graph_size_runtimes.pickled','rb') as pickled:
    runtimes = pickle.load(pickled)
#print(runtimes)
#runtimes[graph_size][method]
x_values = [graph_size for graph_size in runtimes.keys()]
fig,ax = plt.subplots()
for method in method_names:
	y_values = [runtimes[graph_size][method] for graph_size in x_values]
	print(method)
	for point in zip(x_values,y_values):
		print(point)
	ax.plot(x_values,
		y_values,
		label=method)
ax.set_xlabel('Graph Size (# nodes)')
ax.set_ylabel('Time (s)')
ax.set_title('Run Time Versus Graph Size')
ax.set_xlim(3,128)
ax.set_xticks([3]+[i for i in range(10,129,10)])
ax.set_xticklabels([3]+[i for i in range(10,129,10)])
ax.set_yticks([i*0.01 for i in range(0,110,10)])
ax.set_yticklabels([f'{i*0.01:.3}' for i in range(0,110,10)])
ax.grid()
ax.legend()
plt.show()'''
#*******************************Pipe Depth**************************************
'''with open('pipe_depth_runtimes.pickled','rb') as pickled:
        depth_runtimes = pickle.load(pickled)
#print(depth_runtimes)
#depth_runtimes[pipe_depth][method]
x_values = [pipe_depth for pipe_depth in depth_runtimes.keys()]
fig,ax = plt.subplots()
for method in method_names:
	y_values = [depth_runtimes[depth][method] for depth in x_values]
	print(method)
	for point in zip(x_values,y_values):
		print(point)
	ax.plot(x_values,
		y_values,
		label=method)
ax.set_xlabel('Pipeline Depth (# Stages)')
ax.set_ylabel('Time (s)')
ax.set_title('Run Time Versus Pipeline Depth')
ax.set_xlim(1,63)
ax.set_xticks([1]+[i for i in range(4,68,4)])
ax.set_xticklabels([1]+[i for i in range(4,68,4)])
ax.set_yticks([i*0.01 for i in range(0,110,10)])
ax.set_yticklabels([f'{i*0.01:.3}' for i in range(0,110,10)])
ax.grid()
ax.legend()
plt.show()'''
#************************Performance,fast edge pct******************************
with open('performance_fast_edge_pct.pickled','rb') as picklein:
    results_for_pct = pickle.load(picklein)
    x_values = [pct for pct in results_for_pct.keys()]
for method in method_names:
	y_values = [mean(res[method]) for pct,res in results_for_pct.items()]
	print(method)
	for point in zip(x_values,y_values):
		print(point)
	ax.plot(x_values,
		y_values,
		label=method)
'''ax.set_xlabel('Pipeline Depth (# Stages)')
ax.set_ylabel('Time (s)')
ax.set_title('Run Time Versus Pipeline Depth')
ax.set_xlim(1,63)
ax.set_xticks([1]+[i for i in range(4,68,4)])
ax.set_xticklabels([1]+[i for i in range(4,68,4)])
ax.set_yticks([i*0.01 for i in range(0,110,10)])
ax.set_yticklabels([f'{i*0.01:.3}' for i in range(0,110,10)])'''
ax.grid()
ax.legend()
plt.show()