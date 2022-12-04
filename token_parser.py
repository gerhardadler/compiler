from dataclasses import dataclass

from collections import UserList
from expression import Expression
from compiler import registers
from type import Type


@dataclass
class VarType:
    name: str
    size: int
    def __post_init__(self):
        self.size_specifier = size_to_specifier(self.size)


@dataclass
class Var:
    name: str
    var_type: VarType
    rbp_diff: int
    address_of: bool = False
    type: Type = Type.VAR


@dataclass
class VarDeclaration:
    var: Var
    assignment_operator: 
    return {
        "type": "var_declaration",
        "var": var,
        "assignment_operator": assignment_operator,
        "expression": Expression(stack)
    }


@dataclass
class FunctionDeclaration:
    name: str
    parameters: list # of parameters
    type: Type = Type.FUNC_DECLARATION
    body: list = []


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
outer_scope_vars = [] # arguments
inner_scope_vars = [] # local vars
funcs = []
current_func = None
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
    global inner_scope_vars
    global outer_scope_vars
    global funcs
    i = 0
    while i < len(stack):
        if stack[i]["type"] == "var_name":
            for scope_var in inner_scope_vars + outer_scope_vars:
                if stack[i]["name"] == scope_var["name"]:
                    stack[i] = scope_var.copy()
                    if stack[i - 1]["type"] == "address_of":
                        stack[i]["address_of"] = True
                        stack.pop(i - 1) # removes address_of specifier
        elif stack[i-1]["type"] != "func_declaration" and stack[i]["type"] == "func_name":
            if stack[i]["name"] not in [func["name"] for func in funcs]:
                raise Exception("func name not defined")
            bracket_count = 0
            func_nodes = []
            while True:
                func_node = stack.pop(i)
                if func_node["name"] == "(":
                    bracket_count += 1
                elif func_node["name"] == ")":
                    bracket_count -= 1
                func_nodes.append(func_node)
                if (bracket_count == 0 and func_node["name"] == ")"):
                    break
            stack.insert(i, parse_func_reference(func_nodes))
        i += 1
    return stack


def inner_scope_rbp_diff(var_size):
    global inner_scope_vars
    rbp_diff = 0
    for var in inner_scope_vars:
        rbp_diff -= var["size"]
    rbp_diff -= var_size
    rbp_diff //= 8
    return rbp_diff

def outer_scope_rbp_diff():
    global outer_scope_vars
    rbp_diff = 0
    for var in outer_scope_vars:
        rbp_diff += var["size"]
    rbp_diff += 128 # because rbp is shifted 128 bits
    rbp_diff //= 8
    return rbp_diff

def parse_var_declaration(stack):
    global outer_scope_vars
    global inner_scope_vars
    if stack[1]["type"] != "var_name":
        exit("syntax error 1")
    if stack[2]["type"] != "assignment_operator":
        exit("syntax error 2")

    var_type = stack.pop(0)
    var_name = stack.pop(0)["name"]
    assignment_operator = stack.pop(0)

    var = create_var_node(var_type, var_name, inner_scope_rbp_diff(var_type["size"]))
    inner_scope_vars.append(var)

    stack = add_stack_info(stack)

    return {
        "type": "var_declaration",
        "var": var,
        "assignment_operator": assignment_operator,
        "expression": Expression(stack)
    }

def parse_var_reference(stack):
    global outer_scope_vars
    global inner_scope_vars
    if stack[1]["type"] != "assignment_operator":
        exit("syntax error4")

    stack = add_stack_info(stack)

    var = stack.pop(0)
    assignment_operator = stack.pop(0)

    return {
        "type": "var_assignment",
        "var": var,
        "assignment_operator": assignment_operator,
        "expression": Expression(stack)
    }

def parse_func_declaration(stack):
    global outer_scope_vars
    global inner_scope_vars
    global funcs
    global current_func

    outer_scope_vars = [] # resets outer vars (parameters)

    stack.pop(0) # gets rid of func definer
    func_name = stack.pop(0)["name"]

    stack = [node for node in stack if node["type"] not in ["comma", "round_bracket", "address_of"]]
    
    stack_iter = iter(stack)
    var_types_and_names = list(zip(stack_iter, stack_iter)) # type and name in list of tuples
    print(var_types_and_names)

    var_types_and_names.reverse() # reverses to get correct rdp diff

    for type, name in var_types_and_names:
        outer_scope_vars.append(create_var_node(type, name["name"], outer_scope_rbp_diff()))

    outer_scope_vars.reverse() # reverses back to correlate with arguments

    func = {
        "type": "func_declaration",
        "name": func_name,
        "parameters": outer_scope_vars,
        "body": []
    }
    funcs.append(func)
    current_func = func
    inner_scope_vars = [] # resets inner vars
    return func

def parse_func_reference(stack):
    global funcs
    func_name = stack.pop(0)["name"]
    for func in funcs:
        if func_name == func["name"]:
            parameters = func["parameters"]
            break
    else: # if func name isnt declared
        exit("undeclared func name")

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
    func_rsp_offset = -inner_scope_rbp_diff(0)
    parameter_sizes = 0
    for argument, parameter in zip(arguments, parameters):
        parameter_sizes += parameter["size"]
        parameter["rbp_diff"] = inner_scope_rbp_diff(parameter_sizes)
        output_arguments.append({
            "type": "argument_declaration",
            "var": parameter,
            "expression": Expression(argument)
        })
        func_rsp_offset += parameter["size"] // 8

    return {
        "type": "func_reference",
        "name": func_name,
        "arguments": output_arguments,
        "func_rsp_offset": func_rsp_offset
    }

def parse_return(stack, func_name):
    stack.pop(0) # gets rid of return keyword
    if len(stack) == 0:
        stack = [{"type": "number", "name": "0"}]
    else:
        stack = add_stack_info(stack)

    return {
        "type": "return",
        "expression": Expression(stack),
        "current_func_name": func_name
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
    global outer_scope_vars
    global inner_scope_vars

    stack.pop(0) # removes if

    stack = add_stack_info(stack)


    return {
        "type": "if",
        "expression": Expression(stack),
        "body": []
    }

def token_parser(tokens):
    global syntax_tree
    global outer_scope_vars
    global inner_scope_vars
    global stack
    global current_func
    for token in tokens:
        if token["type"] in ["semicolon", "curly_bracket"]:
            if token["name"] == "}":
                syntax_tree.step_down_block()
            elif stack[0]["type"] == "type_declaration":
                syntax_tree.add_node(parse_var_declaration(stack))
            elif stack[0]["type"] == "var_name":
                syntax_tree.add_node(parse_var_reference(stack))
            elif stack[0]["type"] == "func_declaration":
                syntax_tree.add_block(parse_func_declaration(stack))
            elif stack[0]["type"] == "func_name":
                syntax_tree.add_node(parse_func_reference(stack))
            elif stack[0]["type"] == "return":
                syntax_tree.add_node(parse_return(stack, current_func["name"]))
            elif stack[0]["type"] == "syscall":
                syntax_tree.add_node(parse_syscall(stack))
            elif stack[0]["type"] == "if":
                syntax_tree.add_block(parse_if(stack))
            stack = []
        else:
            stack.append(token)
    return syntax_tree