from extract_base_graph import *
from source_code_parser import count_loc
import math
import csv


ignore_files = []


def get_dataset_data(project_path):
    data_path = project_path + '/candidate_Long_Methods.csv'
    res = []
    with open(data_path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            # print(row)
            if len(row) > 1:
                row_data = [row[0].split(';')[0], row[1].split(';')[0]]
                if not row[1].split(';')[0] in ignore_files:
                	res.append(row_data)

    # print(len(res), res)
    return res



def get_candidate_functions(graph_res, project_path):
    
    inter_closeness = graph_res['internal_closeness']
    exter_closeness = graph_res['external_closeness']
    last_id = graph_res['last_id']
    internal_g = graph_res['internal_graph']
    exeternal_g = graph_res['external_graph']
    observed = []
    total_counter_nim = 0
    total_counter_1 = 0
    total_counter_2 = 0
    total_counter_3 = 0
    total_counter_4 = 0
    same_methods_counter_nim = 0
    same_methods_counter_1 = 0
    same_methods_counter_2 = 0
    same_methods_counter_3 = 0
    same_methods_counter_4 = 0

    # dataset = get_dataset_data(project_path)

    candidate_funcions = []

    for node_id in range(last_id):

        try:
            method_hir = internal_g.nodes[node_id]['name']
        except:
            method_hir = exeternal_g.nodes[node_id]['name']

        if method_hir in observed:
            continue

        observed.append(method_hir)

        DE = (inter_closeness.get(node_id, 0) + 1) / (exter_closeness.get(node_id, 0) + 1)
        
        method_parents = method_hir.split('->')
        
        num_loc = count_loc(method_parents[-2], method_parents[-1], project_path)

        if num_loc is not None:

            res = DE + math.exp((num_loc-40)/10)

            if res > 0.5:
                if '$' in method_parents[-2]:
                    class_name = method_parents[-2].split('$')[0]
                else:
                    class_name = method_parents[-2]

                total_counter_nim += 1
                candidate_funcions.append(method_parents)

            if res > 1:
                if '$' in method_parents[-2]:
                    class_name = method_parents[-2].split('$')[0]
                else:
                    class_name = method_parents[-2]

                total_counter_1 += 1

            if res > 2:
                if '$' in method_parents[-2]:
                    class_name = method_parents[-2].split('$')[0]
                else:
                    class_name = method_parents[-2]

                total_counter_2 += 1

            if res > 3:
                if '$' in method_parents[-2]:
                    class_name = method_parents[-2].split('$')[0]
                else:
                    class_name = method_parents[-2]

                total_counter_3 += 1

            if res > 4:
                if '$' in method_parents[-2]:
                    class_name = method_parents[-2].split('$')[0]
                else:
                    class_name = method_parents[-2]

                total_counter_4 += 1

    return candidate_funcions
