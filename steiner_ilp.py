from gurobipy import Model,LinExpr
from itertools import chain,product,combinations
from random import sample

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
       T = set of terminals in V
       root = root node of Steiner tree
    """
    V_less_root = set(V).difference(set([root]))
    subsets_no_root =  map(lambda u:set(u).union(set([root])),powerset(V_less_root))
    return (subset for subset in subsets_no_root if subset.intersection(T) != T)

def gen_cutsets(V,T,E,root=0):
    """Generator to produce Steiner cut inequalities for constraints
    
    V: nodes
    T: terminals (subset of nodes)
    E: directed edges
    root: terminal to act as the root of the Steiner tree
    
    These sets are the different delta(W)s in the ILP formulation presented
    Kock and Martin in 1998. See docstring for 'bidirected_steiner_tree' for
    details about the paper.
    """
    for s in gen_S(set(V),set(T),root=root):
        pdp = set((e for e in possible_delta_p(s,set(V))))
        yield pdp.intersection(E)

def print_edge_attr(g,attr='weight',w=None):
    """Print edge attributes for a given networkx graph
    
    g: a NetworkX graph object
    attr: attribute key
    w: only print attributes with this value
    """
    for e in g.edges:
        val = g.get_edge_data(*e)[attr]
        if not w or val == w:
            print(f'{e}:{val}')

def bidirected_steiner_tree(V,E,T,weights):
    """Find a minimum-weight Steiner tree
    
    V: an iterable of integers representing nodes
    E: an iterable contain tuples of nodes (edges)
    T: a subset of V that the Steiner tree must include
    weights: a dict whose keys are edge tuples
    
    Based on the bidirected formulation presented in "Solving Steiner tree 
    problems in graphs to optimality" by Thorsten Koch and Alexander Martin
    in "Networks" volume 32,1998.
    """
    if not set(T).issubset(V):
        raise KeyError(f'Terminals not all in V:{set(V).symmetric_difference(T)}')
    A = set(E).union(set(tuple(reversed(e)) for e in E))
    for e in A:
        if e not in weights.keys():
            weights[e] = weights[reversed(e)]
    root = sample(T,1)[0]
    m = Model('steiner')
    d = m.addVars(A,vtype=GRB.BINARY,name='d')
    for s in gen_cutsets(V,set(T).difference(set([root])),A,root=root):
        l = LinExpr()
        for t in s:
            l.add(d[t[0],t[1]])
        c = m.addConstr(lhs=l,sense=GRB.GREATER_EQUAL,rhs=1)
    obj = m.setObjective(d.prod(weights),sense=GRB.MINIMIZE)
    m.optimize()
    d_vars = m.getAttr('x',d)
    #sorted so edges are always between ascending vertices
    steiner_edges = set(tuple(sorted(e)) for e in d_vars if d_vars[e] > 0)
    steiner_vertices = set(chain.from_iterable(steiner_edges))
    return steiner_vertices,steiner_edges,m
