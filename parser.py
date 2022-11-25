from expression import Expression
from compiler import registers

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

def add_stack_info(stack):
    global inner_scope_variables
    global outer_scope_variables
    global functions
    i = 0
    while i < len(stack):
        if stack[i]["type"] == "variable_name":
            for scope_variable in inner_scope_variables + outer_scope_variables:
                if stack[i]["name"] == scope_variable["name"]:
                    stack[i] = scope_variable.copy()
                    if stack[i - 1]["type"] == "address_of":
                        stack[i]["address_of"] = True
                        stack.pop(i - 1) # removes address_of specifier
        elif stack[i-1]["type"] != "function_declaration" and stack[i]["type"] == "function_name":
            if stack[i]["name"] not in [function["name"] for function in functions]:
                raise Exception("function name not defined")
            bracket_count = 0
            function_nodes = []
            while True:
                function_node = stack.pop(i)
                if function_node["name"] == "(":
                    bracket_count += 1
                elif function_node["name"] == ")":
                    bracket_count -= 1
                function_nodes.append(function_node)
                if (bracket_count == 0 and function_node["name"] == ")"):
                    break
            stack.insert(i, parse_function_call(function_nodes)) # maybe infinite loop idkz
        i += 1
    return stack


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
    rbp_diff += 128 # because rbp is shifted 128 bits
    rbp_diff //= 8
    return rbp_diff

def create_variable_node(variable_type, variable_name, scope_rbp_diff):
    return {
        "type": "variable_name",
        "name": variable_name,
        "variable_type": variable_type["name"],
        "size": variable_type["size"],
        "size_specifier": size_to_specifier(variable_type["size"]),
        "rbp_diff": scope_rbp_diff,
        "address_of": False
    }

def parse_variable_declaration(stack):
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    if stack[1]["type"] != "variable_name":
        exit("syntax error 1")
    if stack[2]["name"] != "=":
        exit("syntax error 2")
    if stack[3]["type"] not in ["number", "variable_name", "round_bracket", "function_name"]:
        exit("syntax error 3")

    variable_type = stack.pop(0)
    variable_name = stack[0]["name"]

    variable = create_variable_node(variable_type, variable_name, inner_scope_rbp_diff(variable_type["size"]))
    inner_scope_variables.append(variable)

    stack = add_stack_info(stack)

    return {
        "type": "variable_declaration",
        "expression": Expression(stack)
    }

def parse_variable_reference(stack):
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    if stack[1]["type"] != "assignment_operator":
        exit("syntax error4")

    stack = add_stack_info(stack)

    return {
        "type": "variable_assignment",
        "expression": Expression(stack)
    }

def parse_function_declaration(stack):
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global functions
    global current_block

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
        "type": "function_declaration",
        "name": function_name,
        "parameters": outer_scope_variables,
        "body": []
    }
    functions.append(function)
    current_block += '[-1]["body"]'
    inner_scope_variables = [] # resets inner variables
    return function

def parse_function_call(stack):
    global syntax_tree
    global functions
    global current_block
    function_name = stack.pop(0)["name"]
    for function in functions:
        if function_name == function["name"]:
            parameters = function["parameters"]
            break
    else: # if function name isnt declared
        exit("undeclared function name")

    stack = add_stack_info(stack)
    arguments = []
    arguments.append([])
    for node in stack:
        if node["type"] == "round_bracket":
            continue
        elif node["type"] == "comma":
            arguments.append([])
        else:
            arguments[-1].append(node)

    if len(parameters) != len(arguments):
        exit("unmatching parameters and arguments")
    
    output_arguments = []
    function_rsp_offset = -inner_scope_rbp_diff(0)
    for argument, parameter in zip(arguments, parameters):
        expression = argument
        parameter["rbp_diff"] = inner_scope_rbp_diff(parameter["size"])
        expression.insert(0, parameter)
        expression.insert(1, {"name": "=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "mov"})
        output_arguments.append({
            "type": "argument_declaration",
            "expression": Expression(expression)
        })
        function_rsp_offset += parameter["size"] // 8
        # arguments_size = 0
        # for output_argument in output_arguments:
        #     arguments_size += output_argument["parameter_size"]
        # if argument["type"] == "variable_name":
        #     for variable in scope_variables:
        #         if variable["name"] == argument["name"]:
        #             output_arguments.append({
        #                 "type": "variable_name",
        #                 "name": variable["name"],
        #                 "variable_type": variable["variable_type"],
        #                 "address_of": False,
        #                 "size": argument["size"],
        #                 "size_specifier": size_to_specifier(argument["size"]),
        #                 "rbp_diff": argument["rbp_diff"],
        #                 "parameter_size": parameter["size"],
        #                 "parameter_size_specifier": size_to_specifier(parameter["size"]),
        #                 "argument_rbp_diff": inner_scope_rbp_diff(arguments_size + parameter["size"])
        #             })
        #             break
        #     else: # if variable not in scope
        #         exit("variable not declared")
        # elif argument["type"] == "number":
        #     output_arguments.append({
        #         "type": "number",
        #         "name": argument["name"],
        #         "parameter_size": parameter["size"],
        #         "parameter_size_specifier": size_to_specifier(parameter["size"]),
        #         "argument_rbp_diff": inner_scope_rbp_diff(arguments_size + parameter["size"])
        #     })
        # else:
        #     exit("type not supported for argument")

    return {
        "type": "function_reference",
        "name": function_name,
        "arguments": output_arguments,
        "function_rsp_offset": function_rsp_offset
    }

def parse_syscall(stack):
    global syntax_tree
    global current_block
    stack.pop(0) # gets rid of the syscall keyword
    arguments = []

    stack = add_stack_info(stack)
    arguments = []
    arguments.append([])
    for node in stack:
        if node["type"] == "round_bracket":
            continue
        elif node["type"] == "comma":
            arguments.append([])
        else:
            arguments[-1].append(node)
    syscall_registers = [
        registers["rax"],
        registers["rdi"],
        registers["rsi"],
        registers["rdx"],
        registers["r10"],
        registers["r9"],
        registers["r8"]
    ]
    output_arguments = []
    for argument, syscall_register in zip(arguments, syscall_registers):
        expression = argument
        expression.insert(0, syscall_register)
        expression.insert(1, {"name": "=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "mov"})
        output_arguments.append({
            "type": "argument_declaration",
            "expression": Expression(expression)
        })
    # for node in stack:
    #     if node["type"] in ["comma", "address_of"]:
    #         continue
    #     elif node["name"] == "(":
    #         continue
    #     elif node["name"] == ")":
    #         break
    #     elif node["type"] == "variable_name":
    #         arguments.append(node)
    #     elif node["type"] == "number":
    #         arguments.append(node)
    #     else:
    #         exit("syntax error12")
    # else: # if no ending bracket
    #     exit("syntax error13")
    return {
        "type": "syscall",
        "arguments": output_arguments
    }

def parse_if(stack):
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block

    stack = add_stack_info(stack)

    current_block += '[-1]["body"]'
    return {
        "type": "if",
        "expression": Expression(stack),
        "body": []
    }

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
                eval("syntax_tree " + current_block).append(parse_variable_declaration(stack))
            elif stack[0]["type"] == "variable_name":
                eval("syntax_tree " + current_block).append(parse_variable_reference(stack))
            elif stack[0]["type"] == "function_declaration":
                eval("syntax_tree " + current_block).append(parse_function_declaration(stack))
            elif stack[0]["type"] == "function_name":
                eval("syntax_tree " + current_block).append(parse_function_call(stack))
            elif stack[0]["type"] == "syscall":
                eval("syntax_tree " + current_block).append(parse_syscall(stack))
            elif stack[0]["type"] == "if":
                eval("syntax_tree " + current_block).append(parse_if(stack))
            stack = []
        else:
            stack.append(token)
    return syntax_tree