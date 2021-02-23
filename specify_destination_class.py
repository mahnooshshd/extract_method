import networkx as nx
from source_code_parser import *
from extract_base_graph import *
from networkx.algorithms.centrality.closeness import closeness_centrality
from networkx.algorithms.centrality.betweenness import betweenness_centrality


def calculate_average_clustering_coefficient(graph):
	cc_value = nx.clustering(graph)
	sum_value = 0
	count = len(list(cc_value.keys()))
	for value in cc_value.keys():
		sum_value += (cc_value[value]/count)

	return sum_value


def get_node(gr, val):
	try:
	    existing_node = gr.nodes[val]
	    return existing_node
	except:
		return None


def get_graph_betweenness(graph):
	closeness = betweenness_centrality(graph)
	return closeness


def get_method_related_classes(internal_graph, external_graph, method_name, class_name):
	hierarchy = '%s->%s'%(class_name, method_name)
	class_list = {}
	for i in list(external_graph.nodes(data=True)):
		if hierarchy in i[1]['name']:
			for neighbour in external_graph.neighbors(i[0]):
				related_class_name = external_graph.nodes[neighbour]['name'].split('->')[-2]
				if related_class_name in class_list.keys():
					class_list[related_class_name] += 1
				else:
					class_list[related_class_name] = 1

	for i in list(internal_graph.nodes(data=True)):
		if hierarchy in i[1]['name']:
			for neighbour in internal_graph.neighbors(i[0]):
				related_class_name = internal_graph.nodes[neighbour]['name'].split('->')[-2]
				if related_class_name in class_list.keys():
					class_list[related_class_name] += 1
				else:
					class_list[related_class_name] = 1
	return class_list



def get_class_related_classes(internal_graph, external_graph, class_name):
	class_list = {}
	for i in list(external_graph.nodes(data=True)):
		if class_name in i[1]['name']:
			for neighbour in external_graph.neighbors(i[0]):
				related_class_name = external_graph.nodes[neighbour]['name'].split('->')[-2]
				if related_class_name in class_list.keys():
					class_list[related_class_name] += 1
				else:
					class_list[related_class_name] = 1

	for i in list(internal_graph.nodes(data=True)):
		if class_name in i[1]['name']:
			for neighbour in internal_graph.neighbors(i[0]):
				related_class_name = internal_graph.nodes[neighbour]['name'].split('->')[-2]
				if related_class_name in class_list.keys():
					class_list[related_class_name] += 1
				else:
					class_list[related_class_name] = 1
	return class_list



def get_class_internal_relation(internal_graph, class_name):
	method_list = {}
	for i in list(internal_graph.nodes(data=True)):
		if class_name in i[1]['name']:
			for neighbour in internal_graph.neighbors(i[0]):
				related_method_name = internal_graph.nodes[neighbour]['name'].split('->')[-1]
				if related_method_name in method_list.keys():
					method_list[related_method_name] += 1
				else:
					method_list[related_method_name] = 1
	return method_list


def get_method_related_methods(internal_graph, external_graph, method_name, class_name):
	hierarchy = '%s->%s'%(class_name, method_name)
	method_list = {}
	for i in list(internal_graph.nodes(data=True)):
		if hierarchy in i[1]['name']:
			for neighbour in internal_graph.neighbors(i[0]):
				related_method_name = internal_graph.nodes[neighbour]['name'].split('->')[-1]
				if related_method_name in method_list.keys():
					method_list[related_method_name] += 1
				else:
					method_list[related_method_name] = 1
	return method_list


def generate_cohesion_graph(internal_graph, class_name):
	cohesion_graph = nx.Graph()
	for i in list(internal_graph.nodes(data=True)):
		if class_name in i[1]['name']:
			method_name = i[1]['name'].split('->')[-1]
			if get_node(cohesion_graph, method_name) is None:
				cohesion_graph.add_node(method_name)
			
			for neighbour in internal_graph.neighbors(i[0]):
				related_method_name = internal_graph.nodes[neighbour]['name'].split('->')[-1]
				
				if get_node(cohesion_graph, related_method_name) is None:
					cohesion_graph.add_node(related_method_name)
				
				if cohesion_graph.has_edge(method_name, related_method_name):
					cohesion_graph[method_name][related_method_name]['weight'] += 1
				else:
					cohesion_graph.add_edge(method_name, related_method_name, weight=1)
	return cohesion_graph



def update_cohesion_graph(cohesion_graph, new_info, method_name):
	if get_node(cohesion_graph, method_name) is None:
		cohesion_graph.add_node(method_name)

	for method in new_info.keys():
		if get_node(cohesion_graph, method) is not None:
			if not cohesion_graph.has_edge(method_name, method):
				cohesion_graph.add_edge(method_name, method)

	return cohesion_graph




def generate_coupling_graph(new_relation_info, old_relation_info, class_name):
	local = nx.Graph()
	local.add_node(class_name)
	for related_name in old_relation_info.keys():
		local.add_node(related_name)
		local.add_edge(class_name, related_name, weight=old_relation_info[related_name])

	old_graph = local

	for related_name in new_relation_info.keys():
		local.add_node(related_name)
		local.add_edge(class_name, related_name, weight=new_relation_info[related_name])

	return old_graph, local




def define_destination_class(graph_data, method_name, class_name):
	internal_graph = graph_data['internal_graph']
	external_graph = graph_data['external_graph']

	new_info = get_method_related_classes(internal_graph, external_graph, method_name, class_name)
	max_portion = -100
	chosen_class = None
	res = {}
	for candidate_class in new_info:
		try:
			old_info = get_class_related_classes(internal_graph, external_graph, candidate_class)
			old_graph, new_graph = generate_coupling_graph(new_info, old_info, candidate_class)	
			new_closeness = get_graph_betweenness(new_graph)[candidate_class]
			old_closeness = get_graph_betweenness(old_graph)[candidate_class]
			cohesion_graph = generate_cohesion_graph(internal_graph, candidate_class)
			old_clustering_coeficient = calculate_average_clustering_coefficient(cohesion_graph)
			new_info = get_method_related_methods(internal_graph, external_graph, method_name, candidate_class)
			cohesion_graph = update_cohesion_graph(cohesion_graph, new_info, candidate_class)
			new_clustering_coeficient = calculate_average_clustering_coefficient(cohesion_graph)
			portion = new_clustering_coeficient/new_closeness
			if portion > max_portion:
				max_portion = portion
				res = {
					'closness':{'old': old_closeness, 'new': new_closeness},
					'clustering_coeficient': {'old': old_clustering_coeficient, 'new': new_clustering_coeficient}
				}
				chosen_class = candidate_class
		except Exception as e:
			continue

	return res, chosen_class
