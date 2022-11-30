from collections import UserList
from expression import Expression
from compiler import registers

class SyntaxTree(UserList):
    def __init__(self):
        self.data = []
        self.parent_blocks = []
        self.current_block = self.data

    def add_block(self, block):
        self.parent_blocks.append(self.current_block)
        self.current_block.append(block)
        self.current_block = self.current_block[-1]["body"]

    def step_down_block(self):
        self.current_block = self.parent_blocks.pop()
    
    def add_node(self, node):
        self.current_block.append(node)

syntax_tree = SyntaxTree()
outer_scope_variables = [] # arguments
inner_scope_variables = [] # local variables
functions = []
current_function = None
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
            stack.insert(i, parse_function_reference(function_nodes))
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
    global outer_scope_variables
    global inner_scope_variables
    if stack[1]["type"] != "variable_name":
        exit("syntax error 1")
    if stack[2]["type"] != "assignment_operator":
        exit("syntax error 2")

    variable_type = stack.pop(0)
    variable_name = stack.pop(0)["name"]
    assignment_operator = stack.pop(0)

    variable = create_variable_node(variable_type, variable_name, inner_scope_rbp_diff(variable_type["size"]))
    inner_scope_variables.append(variable)

    stack = add_stack_info(stack)

    return {
        "type": "variable_declaration",
        "variable": variable,
        "assignment_operator": assignment_operator,
        "expression": Expression(stack)
    }

def parse_variable_reference(stack):
    global outer_scope_variables
    global inner_scope_variables
    if stack[1]["type"] != "assignment_operator":
        exit("syntax error4")

    stack = add_stack_info(stack)

    variable = stack.pop(0)
    assignment_operator = stack.pop(0)

    return {
        "type": "variable_assignment",
        "variable": variable,
        "assignment_operator": assignment_operator,
        "expression": Expression(stack)
    }

def parse_function_declaration(stack):
    global outer_scope_variables
    global inner_scope_variables
    global functions
    global current_function

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
    current_function = function
    inner_scope_variables = [] # resets inner variables
    return function

def parse_function_reference(stack):
    global functions
    function_name = stack.pop(0)["name"]
    for function in functions:
        if function_name == function["name"]:
            parameters = function["parameters"]
            break
    else: # if function name isnt declared
        exit("undeclared function name")

    stack = add_stack_info(stack)
    arguments = []
    for node in stack:
        if node["type"] == "round_bracket":
            continue
        elif node["type"] == "comma":
            arguments.append([])
        else:
            if len(arguments) == 0:
                arguments.append([])
            arguments[-1].append(node)

    print(parameters)
    print(arguments)
    if len(parameters) != len(arguments):
        exit("unmatching parameters and arguments")
    
    output_arguments = []
    function_rsp_offset = -inner_scope_rbp_diff(0)
    parameter_sizes = 0
    for argument, parameter in zip(arguments, parameters):
        parameter_sizes += parameter["size"]
        parameter["rbp_diff"] = inner_scope_rbp_diff(parameter_sizes)
        output_arguments.append({
            "type": "argument_declaration",
            "variable": parameter,
            "expression": Expression(argument)
        })
        function_rsp_offset += parameter["size"] // 8

    return {
        "type": "function_reference",
        "name": function_name,
        "arguments": output_arguments,
        "function_rsp_offset": function_rsp_offset
    }

def parse_return(stack, function_name):
    stack.pop(0) # gets rid of return keyword
    if len(stack) == 0:
        stack = [{"type": "number", "name": "0"}]
    else:
        stack = add_stack_info(stack)

    return {
        "type": "return",
        "expression": Expression(stack),
        "current_function_name": function_name
    }

def parse_syscall(stack):
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
        output_arguments.append({
            "type": "argument_declaration",
            "syscall_register": syscall_register,
            "expression": Expression(expression)
        })
    return {
        "type": "syscall",
        "arguments": output_arguments
    }

def parse_if(stack):
    global outer_scope_variables
    global inner_scope_variables

    stack.pop(0) # removes if

    stack = add_stack_info(stack)


    return {
        "type": "if",
        "expression": Expression(stack),
        "body": []
    }

def parser(tokens):
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global stack
    global current_function
    for token in tokens:
        if token["type"] in ["semicolon", "curly_bracket"]:
            if token["name"] == "}":
                syntax_tree.step_down_block()
            elif stack[0]["type"] == "type_declaration":
                syntax_tree.add_node(parse_variable_declaration(stack))
            elif stack[0]["type"] == "variable_name":
                syntax_tree.add_node(parse_variable_reference(stack))
            elif stack[0]["type"] == "function_declaration":
                syntax_tree.add_block(parse_function_declaration(stack))
            elif stack[0]["type"] == "function_name":
                syntax_tree.add_node(parse_function_reference(stack))
            elif stack[0]["type"] == "return":
                syntax_tree.add_node(parse_return(stack, current_function["name"]))
            elif stack[0]["type"] == "syscall":
                syntax_tree.add_node(parse_syscall(stack))
            elif stack[0]["type"] == "if":
                syntax_tree.add_block(parse_if(stack))
            stack = []
        else:
            stack.append(token)
    return syntax_tree