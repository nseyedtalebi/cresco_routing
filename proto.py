# coding: utf-8
from gurobipy import *
import networkx as nx
g = nx.complete_graph(n=8,create_using=nx.DiGraph())
for edge in g.edges:
    g.add_edge(*edge,weight=10)
fast_links = [(0,5),(5,6),(6,3)]
fast_both = fast_links+[tuple(reversed(link)) for link in fast_links]
g.add_edges_from(fast_both,weight=1)
m = Model('p')
#d_index = [[i,j for i in range(len(g)) for j in range(len(g)) if i!=j]
#d = m.addVars(,vtype=GRB.BINARY,name='d')
d = m.addVars(list(g.edges),vtype=GRB.BINARY,name='d')
y = m.addVars(range(len(g)),vtype=GRB.BINARY,name='y')
u = m.addVars(range(len(g)),vtype=GRB.INTEGER,lb=0,ub=len(g),name='u')
#eights = [g.get_edge_data(i,j)['weight'] for i in range(len(g)) for j in range(len(g)) if i!=j]
vstar = range(1,len(g))
one_e = m.addConstrs((d[i,j] + d[j,i] <= y[j] for i in range(len(g)) for j in vstar if i!=j),'one_e')
#subt = m.addConstrs((len(g)*(d[i,j]+d[j,i]) + u[i] - u[j] <= len(g)*y[i] - y[j] for i in range(len(g)) for j in range(len(g))),name='subt')
subt = m.addConstrs((len(g)*d[i,j] + u[i] - u[j] <= len(g)*y[i] - y[j] for i in range(len(g)) for j in range(len(g)) if i!=j),name='subt')
subt_2 = m.addConstrs((y[j] <= u[j] <= len(g)*y[j] for j in vstar),name='subt_2')
u_0 = m.addConstr(u[0]==0,name='u_0')
y_0  = m.addConstr(y[0] == 1,name='y_0')
one_direction = m.addConstrs((d.sum('*',j) == y[j] for j in vstar),name='one_dir')
fake_c = m.addConstr(y[6] == 1,name='fake_c')
weights = {}
for i in range(len(g)):
    for j in range(len(g)):
        if i!=j:
            weights[i,j] = g.get_edge_data(i,j)['weight']
obj = m.setObjective(d.prod(weights),sense=GRB.MINIMIZE)

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))
