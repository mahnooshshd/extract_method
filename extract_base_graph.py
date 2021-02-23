import networkx as nx
from networkx.algorithms.centrality.closeness import closeness_centrality


def find_node(gr, att, val):
    existing_node = [node for node in gr.nodes(data=True) if node[1][att] == val]
    
    if len(existing_node) == 0:
    	return None

    return existing_node[0][0]


def calculate_closeness(call_file_path):


	call_file = open(call_file_path, 'r+')
	call_content = call_file.read()

	call_lines = call_content.split('\n')

	calls = {}

	internal_g = nx.Graph()
	external_g = nx.Graph()

	class_num = 0

	for line in call_lines:
		if line.startswith('C:') or len(line) < 5:
			continue
		
		caller_part = line.split(' ')[0][2:]
		callee_part = line.split(' ')[1][3:]

		caller_hir = caller_part.split(':')[0].split('.')
		caller_method = caller_part.split(':')[1].split('(')[0]

		caller_hir.append(caller_method)

		callee_hir = callee_part.split(':')[0].split('.')
		callee_method = callee_part.split(':')[1].split('(')[0]

		callee_hir.append(callee_method)

		caller_name = '->'.join(caller_hir)
		callee_name = '->'.join(callee_hir)

		if callee_hir[-2] == caller_hir[-2]:

			caller_num = find_node(internal_g, 'name', caller_name)
			callee_num = find_node(internal_g, 'name', callee_name)

			if caller_num is None:
				caller_num = class_num
				internal_g.add_nodes_from([(caller_num,{'name':caller_name})])
				class_num = class_num + 1

			
			if callee_num is None:
				callee_num = class_num
				internal_g.add_nodes_from([(callee_num,{'name':callee_name})])
				class_num = class_num + 1


			internal_g.add_edge(caller_num, callee_num)

		else:
			caller_num = find_node(external_g, 'name', caller_name)
			callee_num = find_node(external_g, 'name', callee_name)

			if caller_num is None:
				caller_num = class_num
				external_g.add_nodes_from([(caller_num,{'name':caller_name})])
				class_num = class_num + 1

			
			if callee_num is None:
				callee_num = class_num
				external_g.add_nodes_from([(callee_num,{'name':callee_name})])
				class_num = class_num + 1
			
			external_g.add_edge(caller_num, callee_num)


	print(internal_g.number_of_edges())
	print(external_g.number_of_edges())

	internal_closeness = closeness_centrality(internal_g)
	external_closeness = closeness_centrality(external_g)

	res = {
		'internal_closeness': internal_closeness,
		'external_closeness': external_closeness,
		'last_id': class_num,
		'internal_graph': internal_g,
		'external_graph': external_g

	}

	return res
