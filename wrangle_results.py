import pickle

import numpy as np
import matplotlib.pyplot as plt

import placer

#We don't actually want the functions, just the names
method_names = [name for name in placer.prepare_functions(None,None).keys()]
'''#*************************Graph Size********************************************
with open('runtimes.pickled','rb') as pickled:
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
	ax.legend()
plt.show()'''
#*******************************Pipe Depth**************************************
with open('pipe_depth_runtimes.pickled','rb') as pickled:
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
	ax.legend()
plt.show()

#  D U D E! The networkx steiner_tree function computes the metric closure
# and then the MST. I could get much better performance if I just do that myself
# and only compute the metric closure once!