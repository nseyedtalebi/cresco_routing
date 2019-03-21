import pickle

import numpy as np
import matplotlib.pyplot as plt

with open('runtimes.pickled','rb') as pickled:
    runtimes = pickle.load(pickled)
to_plot = [(graph_size,)for graph_size,timing_data in runtimes.items()]
#loop through dict of timing data, use zip with graph size to produce x,y pairs
#for plotting