from expression import Expression

syntax_tree = []
outer_scope_variables = [] # arguments
inner_scope_variables = [] # local variables
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
    for stack_index, node in enumerate(stack):
        if node["type"] == "variable_name":
            for scope_variable in inner_scope_variables + outer_scope_variables:
                if node["name"] == scope_variable["name"]:
                    stack[stack_index] = scope_variable

def inner_scope_rbp_diff():
    global inner_scope_variables
    rbp_diff = 0
    for variable in inner_scope_variables:
        rbp_diff += variable["size"]
    rbp_diff //= 8
    return -rbp_diff

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
        "rbp_diff": scope_rbp_diff if scope_rbp_diff >= 0 else scope_rbp_diff - variable_type["size"] // 8
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

    variable = create_variable_node(variable_type, variable_name, inner_scope_rbp_diff())
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
    global current_block
    global stack
    stack.pop(0) # gets rid of function definer
    function_name = stack.pop(0)["name"]

    current_type = ""
    for node in stack:
        if node["type"] == "comma":
            continue
        elif node["name"] == "(":
            continue
        elif node["name"] == ")":
            break
        elif node["type"] == "type_declaration":
            if not current_type:
                current_type = node
            else:
                exit("syntax error5")
        elif node["type"] == "variable_name":
            if current_type:
                outer_scope_variables.append(create_variable_node(current_type, node["name"], outer_scope_rbp_diff()))
                current_type = ""
            else:
                exit("syntax error6")
        else:
            exit("syntax error7")

    eval("syntax_tree " + current_block).append({
        "type": "function",
        "name": function_name,
        "parameters": outer_scope_variables,
        "body": []
    })
    current_block += '[-1]["body"]'
    inner_scope_variables = []

def parse_function_call():
    global syntax_tree
    global current_block
    global stack
    function_name = stack.pop(0)["name"]
    arguments = []
    for node in stack:
        if node["type"] == "comma":
            continue
        elif node["name"] == "(":
            continue
        elif node["name"] == ")":
            break
        elif node["type"] == "variable_name":
            scope_variables = inner_scope_variables + outer_scope_variables
            for variable in scope_variables:
                if variable["name"] == node["name"]:
                    arguments.append(variable)
                    arguments[-1]["argument_rbp_diff"] = -(len(inner_scope_variables) + len(arguments)) * 4
                    break
            else:
                exit("syntax error8")
        elif node["type"] == "number":
            arguments.append(node)
            arguments[-1]["argument_rbp_diff"] = -(len(inner_scope_variables) + len(arguments)) * 4
        else:
            exit("syntax error9")
    else: # if no ending bracket
        exit("syntax error10")
    eval("syntax_tree " + current_block).append({
        "type": "function_name",
        "name": function_name,
        "arguments": arguments
    })

def parse_syscall():
    global syntax_tree
    global current_block
    global stack
    stack.pop(0) # gets rid of the syscall keyword
    arguments = []
    for node in stack:
        if node["type"] == "comma":
            continue
        elif node["name"] == "(":
            continue
        elif node["name"] == ")":
            break
        elif node["type"] == "variable_name":
            scope_variables = inner_scope_variables + outer_scope_variables
            for variable in scope_variables:
                if variable["name"] == node["name"]:
                    arguments.append(variable)
                    break
            else:
                exit("syntax error11")
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