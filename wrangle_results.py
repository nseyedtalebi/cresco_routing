import pickle

import numpy as np
import matplotlib.pyplot as plt

import placer

with open('runtimes.pickled','rb') as pickled:
    runtimes = pickle.load(pickled)
#print(runtimes)
#runtimes[graph_size][method]
#We don't actually want the functions but I can conveniently get a list of names
method_names = [name for name in placer.prepare_functions(None,None).keys()]
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
plt.show()
#loop through dict of timing data, use zip with graph size to produce x,y pairs
#for plotting