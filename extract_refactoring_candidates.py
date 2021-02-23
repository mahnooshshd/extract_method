import networkx as nx
from source_code_parser import *
from numpy import linalg as LA
import numpy as np


def get_adjacency_matrix(graph):
	matrix = nx.to_numpy_array(graph)
	return matrix



def get_modularity_matrix(graph):
	adjacency_matrix = get_adjacency_matrix(graph)
	shape = adjacency_matrix.shape
	modulairy = np.zeros(shape)
	number_of_edges = graph.number_of_edges()

	for i in range(shape[0]):
		for j in range(shape[1]):
			modulairy[i][j] = adjacency_matrix[i][j] - ((graph.degree[i]*graph.degree[j])/(2*number_of_edges))

	return modulairy


def get_eigenvalues(matrix):
	eigen_values = LA.eigvals(matrix)
	return eigen_values


def refactor_is_possible(eigenvalues):
	for value in eigenvalues:
		if value > 0:
			return True
	return False



def get_starting_points(adjacency_matrix):

	starting_points = []
	for i in range(adjacency_matrix.shape[0]):
		row_sum = 0
		for j in range(adjacency_matrix.shape[1]):
			row_sum += adjacency_matrix[i][j]
		if row_sum <= 5:
			starting_points.append(i)
	return starting_points


def calculate_clustering_coefficient(graph, node):
	cc_value = nx.clustering(graph, node)
	return cc_value


def get_sub_graph(graph, starting_point, loc):
	adjacency_matrix = get_adjacency_matrix(graph)
	extracted_lines = [starting_point]
	external_dependency = []
	shape = adjacency_matrix.shape
	for line in extracted_lines:

		clustering_coefficients = []

		for j in range(shape[1]):
			if adjacency_matrix[line][j] == 2:
				if not j in extracted_lines:
					external_dependency.append(j)

		for i in range(shape[0]):
			
			if adjacency_matrix[i][line] == 1:
				if not i in extracted_lines:
					extracted_lines.append(i)

			if adjacency_matrix[i][line] == 2:
				cc_value = calculate_clustering_coefficient(graph, i)
				clustering_coefficients.append({i:cc_value})

		max_val = None
		for c in clustering_coefficients:
			max_val = {-1:0}
			if list(c.values())[0] > list(max_val.values())[0] :
				max_val = c
		if max_val is not None:
			if not list(c.keys())[0] in extracted_lines:
				extracted_lines.append(list(c.keys())[0])
		
		if len(external_dependency) > 4:
			return extracted_lines

		if len(extracted_lines) > (2*loc)/3:
			return extracted_lines



def in_same_subgraph(node1, node2, sub_graph):
	if node1 in sub_graph and node2 in sub_graph:
		return 1
	return -1


def rank_refactoring_candidates(graph, refactorings):

	refactoring_ranks = {}
	total_edges = graph.size()
	adjacency_matrix = get_adjacency_matrix(graph)
	shape = adjacency_matrix.shape
	counter = 0
	for refactoring in refactorings:
		Q = 0
		for i in range(shape[0]):
			for j in range(shape[1]):
				ki = graph.degree[i]
				kj = graph.degree[j]
				tmp = (adjacency_matrix[i][j]-((ki*kj)/(2*total_edges))) * in_same_subgraph(i,j, refactoring)
				Q += tmp / (2*total_edges)

		refactoring_ranks[counter] = {Q:refactoring}
		counter += 1
	return refactoring_ranks


def get_candidate_refactorings(method_name, class_name, project_path):
	graph = get_code_graph(method_name, class_name, project_path)
	if graph is not None:
		modulairty = get_modularity_matrix(graph)
		eigenvalues = get_eigenvalues(modulairty)
		adjacency_matrix = get_adjacency_matrix(graph)
		loc = count_loc(class_name, method_name, project_path)
		if refactor_is_possible(eigenvalues):
			possible_refactorings = []
			starting_points = get_starting_points(adjacency_matrix)
			for starting in starting_points:
				sub_graph = get_sub_graph(graph, starting, loc)
				
				if sub_graph is not None:
					possible_refactorings.append(sub_graph)
			refactoring_ranks = rank_refactoring_candidates(graph, possible_refactorings)
			return refactoring_ranks, loc
