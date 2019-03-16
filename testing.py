import networkx as nx
import placer

'''def test_placements(print_placements=True):
    test_graph = nx.complete_graph(n=9)
    capacities = {node:0 for node in test_graph.nodes}
    capacities[4] = 10
    base = {'g':test_graph,'slow_edge':100,'fast_edge':1,'capacities':capacities}
    diagonal = {**base,'fast_edges':((0,4),(4,8))}
    shared = {**base,'fast_edges':((4,5),)}
    v_shaped = {**base,'fast_edges':((0,4),(2,4))}
    diag_p = get_placements(get_model(**diagonal)[0],terminals=(0,8),required_capacity=10)[0]
    shared_p = get_placements(get_model(**shared)[0],terminals=(4,5),required_capacity=10)[0]
    v_shaped_p = get_placements(get_model(**v_shaped)[0],terminals=(0,2),required_capacity=10)[0]
    if print_placements:
        for placement in (diag_p,shared_p,v_shaped_p,):
            print(f'{placement.node} {placement.weight} {placement.tree.edges}')
    assert diag_p.node == 4 and diag_p.weight == 2
    assert shared_p.node == 4 and shared_p.weight == 1
    assert v_shaped_p.node == 4 and v_shaped_p.weight == 2'''
def get_model_and_test_spec():
    #inputs for stage 1: 0,1,4
    #stage 1 to be placed at 5
    #inputs for stage 2: 6,7,11,15
    #stage 2 to be placed at 10
    #5 and 10 should have capacity > 0, others all 0
    graph_size=16
    model_params = {'g':nx.complete_graph(n=graph_size),'slow_edge':100,'fast_edge':1}
    model_params['fast_edges'] = [
    (0,5),(1,5),(4,5),#three edges for inputs
    (5,10),#one edge to link stages
    (10,6),(10,7),(10,11),#three edges for inputs
    (10,15)#to the output node
    ]
    model_params['capacities'] = {node:0 for node in model_params['g'].nodes}
    model_params['capacities'][5] = 1
    model_params['capacities'][10] = 1
    model,weights,capacities = placer.get_model(**model_params)
    pipe_spec = [{'input_nodes':[0,1,4],'reqd_capacity':1},#first stage
    {'input_nodes':[6,7,11,15],'reqd_capacity':1}#second stage
    ]
    #return placer.total_weight(model_params['g'])
    return model,pipe_spec

def compare_placements(one,other):
    one_nodes = [p.node for p in one]
    other_nodes = [p.node for p in other]
    return one_nodes == other_nodes

model,spec = get_model_and_test_spec()
it_placements = placer.place_stages_iteratively(spec,model,'mst')
print(it_placements)

model,spec = get_model_and_test_spec()
ind_placements,tree = placer.place_stages_individually(spec,model,'mst')
print(ind_placements)
print(tree)

print(compare_placements(it_placements,ind_placements))
