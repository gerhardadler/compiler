from expression import Expression

syntax_tree = []
outer_scope_variables = [] # arguments
inner_scope_variables = [] # local variables
functions = []
current_block = ""
stack = []

def size_to_specifier(size):
    if size == 8:
        return "byte"
    if size == 16:
        return "word"
    if size == 32:
        return "dword"
    if size == 64:
        return "qword"
    # if nothing matches
    raise Exception("Invalid size")

def stack_add_variable_info():
    for node_index, node in enumerate(stack):
        if node["type"] == "variable_name":
            for scope_variable in inner_scope_variables + outer_scope_variables:
                if node["name"] == scope_variable["name"]:
                    stack[node_index] = scope_variable
                    if stack[node_index - 1]["type"] == "address_of":
                        node["address_off"] = True
                    else:
                        node["address_off"] = False

def inner_scope_rbp_diff(variable_size):
    global inner_scope_variables
    rbp_diff = 0
    for variable in inner_scope_variables:
        rbp_diff -= variable["size"]
    rbp_diff -= variable_size
    rbp_diff //= 8
    return rbp_diff

def outer_scope_rbp_diff():
    global outer_scope_variables
    rbp_diff = 0
    for variable in outer_scope_variables:
        rbp_diff += variable["size"]
    rbp_diff //= 8
    return rbp_diff

def create_variable_node(variable_type, variable_name, scope_rbp_diff):
    return {
        "type": "variable_name",
        "name": variable_name,
        "variable_type": variable_type["name"],
        "size": variable_type["size"],
        "size_specifier": size_to_specifier(variable_type["size"]),
        "rbp_diff": scope_rbp_diff
    }

def parse_variable_declaration():
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    global stack
    if stack[1]["type"] != "variable_name":
        exit("syntax error 1")
    if stack[2]["name"] != "=":
        exit("syntax error 2")
    if stack[3]["type"] not in ["number", "variable_name"]:
        exit("syntax error 3")

    variable_type = stack.pop(0)
    variable_name = stack[0]["name"]

    variable = create_variable_node(variable_type, variable_name, inner_scope_rbp_diff(variable_type["size"]))
    inner_scope_variables.append(variable)

    stack_add_variable_info()

    eval("syntax_tree " + current_block).append({
        "type": "variable_declaration",
        "variable": variable,
        "expression": Expression(stack)
    })

def parse_variable_reference():
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    global stack
    if stack[1]["type"] != "assignment_operator":
        exit("syntax error4")

    stack_add_variable_info()

    eval("syntax_tree " + current_block).append({
        "type": "variable_assignment",
        "expression": Expression(stack)
    })

def parse_function_declaration():
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global functions
    global current_block
    global stack

    outer_scope_variables = [] # resets outer variables (parameters)

    stack.pop(0) # gets rid of function definer
    function_name = stack.pop(0)["name"]

    stack = [node for node in stack if node["type"] not in ["comma", "round_bracket", "address_of"]]
    
    stack_iter = iter(stack)
    variable_types_and_names = list(zip(stack_iter, stack_iter)) # type and name in list of tuples
    print(variable_types_and_names)

    variable_types_and_names.reverse() # reverses to get correct rdp diff

    for type, name in variable_types_and_names:
        outer_scope_variables.append(create_variable_node(type, name["name"], outer_scope_rbp_diff()))

    outer_scope_variables.reverse() # reverses back to correlate with arguments

    function = {
        "type": "function",
        "name": function_name,
        "parameters": outer_scope_variables,
        "body": []
    }
    eval("syntax_tree " + current_block).append(function)
    functions.append(function)
    current_block += '[-1]["body"]'
    inner_scope_variables = [] # resets inner variables

def parse_function_call():
    global syntax_tree
    global functions
    global current_block
    global stack
    function_name = stack.pop(0)["name"]
    for function in functions:
        if function_name == function["name"]:
            parameters = function["parameters"]
            break
    else: # if function name isnt declared
        exit("undeclared function name")

    stack_add_variable_info()
    arguments = [node for node in stack if node["type"] not in ["comma", "round_bracket", "address_of"]]
    print(arguments)
    print(parameters)
    if len(parameters) != len(arguments):
        exit("unmatching parameters and arguments")
    
    scope_variables = inner_scope_variables + outer_scope_variables
    output_arguments = []
    for argument, parameter in zip(arguments, parameters):
        arguments_size = 0
        for output_argument in output_arguments:
            arguments_size += output_argument["parameter_size"]
        if argument["type"] == "variable_name":
            for variable in scope_variables:
                if variable["name"] == argument["name"]:
                    output_arguments.append({
                        "type": "variable_name",
                        "name": variable["name"],
                        "variable_type": variable["variable_type"],
                        "address_of": False,
                        "size": argument["size"],
                        "size_specifier": size_to_specifier(argument["size"]),
                        "rbp_diff": argument["rbp_diff"],
                        "parameter_size": parameter["size"],
                        "parameter_size_specifier": size_to_specifier(parameter["size"]),
                        "argument_rbp_diff": inner_scope_rbp_diff(arguments_size + parameter["size"])
                    })
                    break
            else: # if variable not in scope
                exit("variable not declared")
        elif argument["type"] == "number":
            output_arguments.append({
                "type": "number",
                "name": argument["name"],
                "parameter_size": parameter["size"],
                "parameter_size_specifier": size_to_specifier(parameter["size"]),
                "argument_rbp_diff": inner_scope_rbp_diff(arguments_size + parameter["size"])
            })
        else:
            exit("type not supported for argument")

    eval("syntax_tree " + current_block).append({
        "type": "function_name",
        "name": function_name,
        "arguments": output_arguments
    })

def parse_syscall():
    global syntax_tree
    global current_block
    global stack
    stack.pop(0) # gets rid of the syscall keyword
    arguments = []

    stack_add_variable_info()

    for node in stack:
        if node["type"] in ["comma", "address_of"]:
            continue
        elif node["name"] == "(":
            continue
        elif node["name"] == ")":
            break
        elif node["type"] == "variable_name":
            arguments.append(node)
        elif node["type"] == "number":
            arguments.append(node)
        else:
            exit("syntax error12")
    else: # if no ending bracket
        exit("syntax error13")
    eval("syntax_tree " + current_block).append({
        "type": "syscall",
        "arguments": arguments
    })

def parse_if():
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    global stack

    stack_add_variable_info()

    eval("syntax_tree " + current_block).append({
        "type": "if",
        "expression": Expression(stack),
        "body": []
    })
    current_block += '[-1]["body"]'

def parser(tokens):
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    global stack
    for token in tokens:
        if token["type"] in ["semicolon", "curly_bracket"]:
            if token["name"] == "}":
                current_block = current_block[0:-12]
            elif stack[0]["type"] == "type_declaration":
                parse_variable_declaration()
            elif stack[0]["type"] == "variable_name":
                parse_variable_reference()
            elif stack[0]["type"] == "function":
                parse_function_declaration()
            elif stack[0]["type"] == "function_name":
                parse_function_call()
            elif stack[0]["type"] == "syscall":
                parse_syscall()
            elif stack[0]["type"] == "if":
                parse_if()
            stack = []
        else:
            stack.append(token)
    return syntax_tree