import steiner_ilp
import networkx as nx

def get_model(g,slow_edge,fast_edge,fast_edges,capacities):
    fast_edges += tuple(tuple(reversed(edge)) for edge in fast_edges)
    for edge in g.edges:
        if (edge in fast_edges) or (reversed(edge) in fast_edges):
            g.add_edge(*edge,weight=fast_edge)
        else:
            g.add_edge(*edge,weight=slow_edge)
    for node in g.nodes:
        g.nodes[node]['capacity']=capacities[node]
        #randint(ccap_low,ccap_hi)
    weights = {}
    for i in range(len(g)):
        for j in range(len(g)):
            if i!=j:
                weights[i,j] = g.get_edge_data(i,j)['weight']
    #uniform distr capacities
    capacities = g.nodes.data()
    return g,weights,capacities

def find_optimal_stage(V,E,T,weights,capacities,required):
    models = {}
    for v in V:
        if capacities[v] >= required:
            sv,se,models[v] = steiner_ilp.bidirected_steiner_tree(set(V),set(E),set(T).union(set((v,))),weights=weights)
    return models[min(models,key=lambda m:float(models[m].getAttr('objval')))],models

#best_model,models = find_optimal_stage(g.nodes,g.edges,set((2,6)),weights,capacities,required_capacity)
#graph_size = 32 ran out of memory