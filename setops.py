import networkx as nx
import random
from gurobipy import *
from itertools import chain,product,combinations
from random import sample
from networkx.algorithms.approximation.steinertree import steiner_tree

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

def possible_delta_p(S,V):
    """Get all possible delta_p given a set of nodes V and  S a subset of powerset(V)
    
    S = A subset of powerset(V) where each s in S contains the root node and s.intersect(T) != T
    V = A set of nodes
    returns: a generator that
    """
    V_minus_S = set(V).difference(set(S))
    return (tuple((i,j)) for i,j in product(S,V_minus_S))

def gen_S(V,T,root):
    """Get a generator for the set S

       V = input nodes
       T = set of terminals in V/{root}
       root = root node of Steiner tree
    """
    V_less_root = set(V).difference(set([root]))
    subsets_no_root =  map(lambda u:set(u).union(set([root])),powerset(V_less_root))
    return (subset for subset in subsets_no_root if subset.intersection(T) != T)

'''def delta_p(V,T,E,root=0):
    for s in gen_S(set(V),set(T)):
        possible_delta_ps = set((e for e in possible_delta_p(s,set(V))))
        for e in possible_delta_ps:
            if e in E:
                yield e'''

def gen_cutsets(V,T,E,root=0):
    for s in gen_S(set(V),set(T),root=root):
        pdp = set((e for e in possible_delta_p(s,set(V))))
        yield pdp.intersection(E)

def print_edge_attr(g,attr='weight',w=None):
    for e in g.edges:
        val = g.get_edge_data(*e)[attr]
        if not w or val == w:
            print(f'{e}:{val}')

graph_size = 16
g = nx.complete_graph(n=graph_size,create_using=nx.DiGraph())
u = nx.complete_graph(n=graph_size)
slow_edge = 100
fast_edge=  1
num_fast = 16
num_terminals = 3
fast_edges = sample(tuple(u.edges),num_fast)
terminals = sample(list(u.nodes()),num_terminals)
root = sample(terminals,1)[0]
fast_dir_edges = fast_edges+[tuple(reversed(e)) for e in fast_edges]
for edge in g.edges:
    g.add_edge(*edge,weight= fast_edge if edge in fast_dir_edges else slow_edge)
for edge in u.edges:
    u.add_edge(*edge,weight= fast_edge if edge in fast_edges else slow_edge)

st = steiner_tree(u,terminals)
m = Model('steiner')
d = m.addVars(list(g.edges),vtype=GRB.BINARY,name='d')
for s in gen_cutsets(g.nodes,set(terminals).difference(set([root])),g.edges,root=root):
    l = LinExpr()
    for t in s:
        l.add(d[t[0],t[1]])
    #print(l)
    c = m.addConstr(lhs=l,sense=GRB.GREATER_EQUAL,rhs=1)
weights = {}
for i in range(len(g)):
    for j in range(len(g)):
        if i!=j:
            weights[i,j] = g.get_edge_data(i,j)['weight']
obj = m.setObjective(d.prod(weights),sense=GRB.MINIMIZE)
m.optimize()
print(st.edges)
d_vars = m.getAttr('x',d)
m_edges = [k for k in d_vars if d_vars[k] > 0]

