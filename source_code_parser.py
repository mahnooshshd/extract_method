import glob
import re
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt



control_dep_weight = 1
data_dep_weight = 2


def get_file_path(class_name, project_path):
	if '$' in class_name:
		class_name = class_name.split('$')[0]

	
	file_path =  Path(project_path).rglob(class_name + '.java')

	for f in file_path:
		return f.absolute()

	return None


def count_loc(class_name, method_name, project_path):

	file_path = get_file_path(class_name, project_path)

	if file_path is None:
		return None

	source_lines = open(file_path, 'r').readlines()
	method_found = False
	
	for line in source_lines:
		if '//' in line:
			line = line.split('//')[0]
			

		method_def = re.findall('(public|private|protected) .* %s\(.*'%method_name, line)

		if 'abstract' in line:
			method_def = ''
	
		if len(method_def) > 0:
			method_found = True
			scope_stack = []
			line_counter = 0
			end_of_define = False

		if method_found:
			try:
				if not end_of_define and ')' in line:
					end_of_define = True
				if not end_of_define:
					continue
				if '{' in line and re.search(r"(?<=').*?{.*?(?=')", line) is None and re.search(r'(?<=").*?{.*?(?=")', line) is None:
					scope_stack.append('{')
				
				if '}' in line and re.search(r"(?<=').*?}.*?(?=')", line) is None and re.search(r'(?<=").*?}.*?(?=")', line) is None:
					scope_stack.pop()

				if len(line.strip().replace('\n', '')) > 0:
					line_counter += 1

				if len(scope_stack) == 0 and line_counter > 1:
					return line_counter 
			except Exception as e:
				pass


def get_statement(line):

	if 'else if' in line:
		return 'else if'
	if ('if(' in line or 'if ' in line) and not ';' in line:
		return 'if'
	
	for_search = re.search('for ?\(.+;.*;.*\)', line)
	if for_search:
		return 'for'

	else_search = else_search = re.match('( |})*else( |{)*', line)
	if else_search:
		return 'else'

	try_search = re.match('( |})*try( |{)*', line)
	if try_search:
		return 'try'

	catch_search = re.match('( |})*catch *\(.*\)', line)
	if catch_search:
		return 'catch'

	while_search = re.match('( |})*while *\(.*\)', line)
	if while_search:
		return 'while'

	if '=' in line and not '==' in line and not '=<' in line and not '>=' in line:
		return 'assignment'

	if 'return ' in line:
		return 'return'


def get_if_vars(line):
	parts = re.split('&&|\|\|', line)
	variables = []
	for part in parts:
		clean_part = part.replace('if','').strip()
		inner_parts = re.split('==|>=|<=|!=|>|<', clean_part)
		for inner_part in inner_parts:
			detected_names = re.match('\(?\s*(\w+)[^.|(]*\.?\w*(\(.*\))?.*', inner_part.replace('!',''))
			if detected_names:
				obj_name = detected_names.group(1)
				args_names = detected_names.group(2)
				if args_names is not None:
					arg_names = args_names.replace('(', '').replace(')', '').split(',')
					for arg_name in arg_names:
						if '"' in arg_name or "'" in arg_name:
							continue
						clean_name = re.split('\.|\[', arg_name)[0].strip()
						if len(clean_name) > 0 and clean_name != 'null' and not clean_name.isdigit():
							variables.append(clean_name)
				
				clean_name = obj_name.strip()
				if len(clean_name) > 0 and clean_name != 'null' and not clean_name.isdigit():
					variables.append(clean_name)
	
	return variables


def get_assignment_vars(line):
	variables = []
	parts = line.split('=')
	left_part = parts[0]

	if len(left_part) < len(line):
		def_var = left_part.strip().split(' ')[-1]
		if '.' in def_var:
			def_var = def_var.split('.')[0]
		if '[' in def_var:
			def_var = def_var.split('[')[0]
		right_part = '='.join(parts[1:]).strip()
	else:
		right_part = line.strip()

	inner_parts = re.split('==|>=|<=|!=|>|<|\+|\-|\/|\*|\%', right_part)
	for inner_part in inner_parts:
		detected_names = re.match('\(?\s*(\w+)[^.|(]*\.?\w*(\(.*\))?.*', inner_part.replace('!',''))
		if detected_names:
			obj_name = detected_names.group(1)
			args_names = detected_names.group(2)
			if args_names is not None:
				arg_names = args_names.replace('(', '').replace(')', '').split(',')
				for arg_name in arg_names:
					if '"' in arg_name or "'" in arg_name:
						continue
					clean_name = re.split('\.|\[', arg_name)[0].strip()
					if len(clean_name) > 0 and clean_name != 'null' and not clean_name.isdigit():
						variables.append(clean_name)
			
			clean_name = obj_name.strip()
			if len(clean_name) > 0 and clean_name != 'null' and not clean_name.isdigit():
				variables.append(clean_name)

	return def_var, variables


def get_for_vars(line):
	variables = []
	parts = line.replace('for', '').strip().split(';')
	iterator_var = parts[0].replace('(', '').split('=')[0]
	iterator_var = iterator_var.replace('int', '').strip()
	variables.append(iterator_var)
	cond_vars = re.split('==|>=|<=|!=|>|<', parts[1])
	
	if cond_vars[0].strip() == iterator_var:
		variables.append(cond_vars[1].split('.')[0].strip())
	else:
		variables.append(cond_vars[0].split('.')[0].strip())
	
	return variables


def get_while_vars(line):
	variables = []
	clean_line = line.replace('while','').replace('(', '').replace(')', '').strip()
	detected_names = re.match('\!?(\w+)([^a-zA-z]*(\w*)\.?(\w*)?.*(==|>=|<=|!=|>|<)[^a-zA-Z]*(\w*)\.?(\w*)?.*)?', clean_line)
	if detected_names:
		if detected_names.group(1):
			variables.append(detected_names.group(1).strip())
		if detected_names.group(3):
			variables.append(detected_names.group(3).strip())
		if detected_names.group(6):
			variables.append(detected_names.group(6).strip())

	return variables


def get_return_vars(line):
	variables = []
	right_part = line.replace('return', '').strip()
	detected_names = re.match('\(?\s*(\w+)[^.|(]*\.?\w*(\(.*\))?.*', right_part)
	if detected_names:
		obj_name = detected_names.group(1)
		args_names = detected_names.group(2)
		if args_names is not None:
			arg_names = args_names.replace('(', '').replace(')', '').split(',')
			for arg_name in arg_names:
				if '"' in arg_name or "'" in arg_name:
					continue
				clean_name = re.split('\.|\[', arg_name)[0].strip()
				if len(clean_name) > 0 and clean_name != 'null' and not clean_name.isdigit():
					variables.append(clean_name)
		
		clean_name = obj_name.strip()
		if len(clean_name) > 0 and clean_name != 'null' and not clean_name.isdigit():
			variables.append(clean_name)
	return variables



def get_code_graph(method_name, class_name, project_path):

	file_path = get_file_path(class_name, project_path)

	if file_path is None:

		print('sorry! this class can not be refactored %s'%class_name)
		return None

	# print(file_path)
	source_lines = open(file_path, 'r').readlines()
	method_found = False
	graph = nx.DiGraph()
	
	dependent_blocks = []
	has_start_func = False
	
	for line in source_lines:

		method_def = re.findall('(public|private|protected) .*%s\(.*\).*'%method_name, line)


		if len(method_def) > 0:
			method_found = True
			scope_stack = []
			data_def = {}
			code_lines = []
			line_counter = 0

			scope_stack.append(line_counter)

			if '{' in line:
				has_start_func = True
			
			graph.add_node(line_counter, content=line.strip())
			
			code_lines.append(line)

			input_part = re.search(method_name+'\((.*($\n)?.*)\)', line)
			if input_part:
				input_part = input_part.group(1).replace('\n', '')

			args = input_part.split(',')
			for arg in args:
				var_name = arg.split(' ')[-1].strip()
				# print(var_name)
				data_def[var_name] = line_counter
			continue

		if method_found and not has_start_func:
			if '{' in line:
				has_start_func = True
				continue

		if method_found and has_start_func:
			if len(scope_stack) == 0:
				data = [(u, v) for (u, v, d) in graph.edges(data=True) if d["weight"] == 2]
				control = [(u, v) for (u, v, d) in graph.edges(data=True) if d["weight"] == 1]
				labels = nx.get_edge_attributes(graph, "weight")
				options = {
				    'node_color': 'green',
				    'node_size': 500,
				    'width': 1,
				    'arrowstyle': '-|>',
				    'arrowsize': 10,
				    'with_labels': True,
				    'edge_color':labels
				}
				pos = nx.circular_layout(graph)
				nx.draw_networkx_nodes(graph, pos, node_size=700)
				nx.draw_networkx_edges(graph, pos, edgelist=control, width=3)
				nx.draw_networkx_edges(
				    graph, pos, edgelist=data, width=3, alpha=0.5, edge_color="b", style="dashed"
				)
				nx.draw_networkx_labels(graph, pos, font_size=20, font_family="sans-serif")
				plt.savefig("graph.png") 
				return graph
			
			if len(line.strip().replace('\n', '')) > 0:
				var_list = []
				line_counter += 1
				code_lines.append(line)
				graph.add_node(line_counter, content=line.strip())

				for parent in scope_stack:
					graph.add_weighted_edges_from([(line_counter, parent, control_dep_weight)])

				statement = get_statement(line)

				if statement == 'if':
					#determine variables
					var_list = get_if_vars(line)
					dependent_blocks.append(('if', line_counter))
					
				if statement == 'else if':
					var_list = get_if_vars(line.replace('else ', ''))
					if_line_number = dependent_blocks[-1][1]
					if dependent_blocks[-1][0] != 'if':
						if_line_number = dependent_blocks[-2][1]
					graph.add_weighted_edges_from([(line_counter, if_line_number, control_dep_weight)])
					
				if statement == 'else': 
					#connet to corresponding if condition with control dep edge
					if_line_number = dependent_blocks[-1][1]
					if dependent_blocks[-1][0] != 'if':
						if_line_number = dependent_blocks[-2][1]
						dependent_blocks = dependent_blocks[:-2] + [dependent_blocks[-1]]
					else:
						dependent_blocks = dependent_blocks[:-1]
					graph.add_weighted_edges_from([(line_counter, if_line_number, control_dep_weight)])

				if statement == 'for':
					var_list = get_for_vars(line)
					#detemine iterator var and condition var
					
				if statement == 'while':
					var_list = get_while_vars(line)
					#detemine iterator var and condition var
					
				if statement == 'try':
					dependent_blocks.append(('try', line_counter))
					#hold for connecting to catch
					
				if statement == 'catch':
					try_line_number = dependent_blocks[-1][1]
					if dependent_blocks[-1][0] != 'try':
						try_line_number = dependent_blocks[-2][1]

					graph.add_weighted_edges_from([(line_counter, try_line_number, control_dep_weight)])

				if statement == 'assignment':
					defined_var, var_list = get_assignment_vars(line)
					data_def[defined_var] = line_counter
					#determine vars

				if statement == 'return':
					var_list = get_return_vars(line)
					pass


				for var in var_list:
					def_line = data_def.get(var)
					if def_line is not None:
						graph.add_weighted_edges_from([(line_counter, def_line, data_dep_weight)])


			if '{' in line and re.search(r"(?<=').*?{.*?(?=')", line) is None and re.search(r'(?<=").*?{.*?(?=")', line) is None:
				if len(line.strip()) > 1:
					scope_stack.append(line_counter)
				else:
					scope_stack.append(line_counter - 1)

			
			if '}' in line and re.search(r"(?<=').*?}.*?(?=')", line) is None and re.search(r'(?<=").*?}.*?(?=")', line) is None:

				scope_stack.pop()


def get_method_name(lines, graph):
	input_vars = []
	for index in lines:
		line = graph.nodes[index]['content']
		statement = get_statement(line)
		if statement == 'return':
			return_vars = get_return_vars(line)
			if len(return_vars) > 0:
				return 'get_%s'%return_vars[0]

		if statement == 'if':
			#determine variables
			var_list = get_if_vars(line)
			if len(var_list) > 0:
				input_vars.append(var_list[0])
			

		if statement == 'for':
			var_list = get_for_vars(line)
			if len(var_list) > 0:
				input_vars.append(var_list[0])
			
		if statement == 'while':
			var_list = get_while_vars(line)
			if len(var_list) > 0:
				input_vars.append(var_list[0])

		if statement == 'assignment':
			defined_var, var_list = get_assignment_vars(line)
			if len(var_list) > 0:
				input_vars.append(var_list[0])
	if len(input_vars) > 0:
		return 'handle_%s'%input_vars[0]
