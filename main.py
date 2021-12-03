from extract_base_graph import *
from get_candidates import *
from extract_refactoring_candidates import *
from specify_destination_class import *
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime
import sys
import json
from alive_progress import alive_bar
import os

def generate_call_file(project_dir_name, projetc_jar_file):
    os.system("java -jar javacg-0.1-SNAPSHOT-static.jar %s > %s/call.txt"%(projetc_jar_file, project_dir_name))


def get_line_contents(line_numbers, graph):
    result = []
    for index in line_numbers:
        line = graph.nodes[index]['content']
        result.append(line)
    return result


def plot_data(classes_data, project_dir_name):
    labels = []
    old_values = []
    new_values = []

    counter = 0
    pos_counter = 0
    negative_counter = 0
    for data in classes_data:
        
        old = round(data['clustering_coeficient']['old'], 2)
        new = round(data['clustering_coeficient']['new'], 2)
        if new >= old:
            pos_counter += 1
        else:
            negative_counter += 1

        if new >0 and old>0:
            labels.append('C%s'%counter)
            old_values.append(old)
            new_values.append(new)
            counter += 1


    # print(pos_counter, negative_counter, pos_counter+negative_counter)
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, old_values, width, label='Before refactoring')
    rects2 = ax.bar(x + width/2, new_values, width, label='After refactoring')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Cohesion')
    ax.set_title(project_dir_name)
    ax.legend()

    fig.tight_layout()
    fig.savefig("%s_clustering_coeficient.png"%project_dir_name, dpi=300)


def plot_line_numbers(line_numbers, project_dir_name):

    old_line = []
    new_line = []

    
    for number in line_numbers:
        old_line.append(number[0])
        new_line.append(number[0]-number[1])

    x = np.arange(len(old_line))

    fig, ax = plt.subplots()
    line1, = ax.plot(x, old_line, 'o-', label='Before refactoring')
    line2, = ax.plot(x, new_line, 'o-', label='Ater refactoring')

    ax.set_title('project_dir_name')
    ax.set_ylabel('Number of lines')
    ax.legend()
    fig.savefig("%s_lines.png"%project_dir_name, dpi=300)

def main():
    start = datetime.datetime.now()
    project_dir_name = sys.argv[1]
    projetc_jar_file = sys.argv[2]
    generate_call_file(project_dir_name, projetc_jar_file)
    call_file_path = '%s/call.txt'%project_dir_name
    project_path = './%s'%project_dir_name
    project_name = project_dir_name.split('/')[0]
    print('Fetching project data...')
    graph_res = calculate_closeness(call_file_path)
    candidate_functions = get_candidate_functions(graph_res, project_path)
    ranked_refactprings = []
    new_classes_info = []
    line_numbers = []
    json_output = []
    with alive_bar(len(candidate_functions)) as bar:
        for function in candidate_functions[:20]:
            bar()
            function_refactoring_res = get_candidate_refactorings(function[-1], function[-2], project_path)
            if function_refactoring_res is not None:
                function_refactoring = function_refactoring_res[0]
                loc = function_refactoring_res[1]
                method_graph = function_refactoring_res[2]
                max_rank = -100
                index = -1
                for rank in function_refactoring.keys():
                    if rank is not None:
                        key = list(function_refactoring[rank].keys())[0]
                        if key > max_rank and key > 0:
                            max_rank = key
                            index = rank
                if max_rank > 0:
                    refactored_lines = None
                    chosen_refactoring = function_refactoring[index][max_rank]
                    # print('chosen refactor for method: %s class: %s'%(function[-1], function[-2]), chosen_refactoring)
                    print('method %s of class %s has been refactored'%(function[-1], function[-2]))
                    method_name = get_method_name(chosen_refactoring, method_graph)
                    # print('name for chosen refactoring: %s'%method_name)
                    class_data, new_class = define_destination_class(graph_res, function[-1], function[-2])
                    if new_class is not None and class_data is not None:
                        # print('new class is %s --- %s'%(new_class, class_data))
                        print('----------------------------------')
                        class_data['name'] = new_class
                        new_classes_info.append(class_data)
                        line_numbers.append((loc, len(chosen_refactoring)))
                        refactored_lines = get_line_contents(chosen_refactoring, method_graph)
                    
                    output_obj = {
                        'class': function[-2],
                        'method': function[-1],
                        'destination_class': new_class,
                        'method_name': method_name,
                        'extracted_line_numbers': chosen_refactoring,
                        'extracted_lines': refactored_lines
                    }
                    json_output.append(output_obj)
                    

    os.makedirs('output', exist_ok=True)
    output_file = open('output/%s.json'%project_name, 'w+')
    output_file.write(json.dumps(json_output, indent = 4))
    last = datetime.datetime.now()
    plot_data(new_classes_info, project_dir_name)
    plot_line_numbers(line_numbers, project_dir_name)


main()
