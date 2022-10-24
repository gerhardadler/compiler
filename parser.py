from expression import Expression

syntax_tree = []
outer_scope_variables = [] # arguments
inner_scope_variables = [] # local variables
current_block = ""
stack = []

def parse_variable_declaration():
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    global stack
    if stack[1]["type"] != "variable_name":
        exit("syntax error")
    if stack[2]["name"] != "=":
        exit("syntax error")
    if stack[3]["type"] not in ["number", "variable_name"]:
        exit("syntax_error")

    variable_type = stack.pop(0)["name"]
    variable_name = stack[0]["name"]

    inner_scope_variables.append({
        "type": "variable_name",
        "name": variable_name,
        "size": 32,
        "rbp_diff": -(len(inner_scope_variables) + 1) * 4
    })

    eval("syntax_tree " + current_block).append({
        "type": "variable_declaration",
        "variable_type": variable_type,
        "expression": Expression(stack, inner_scope_variables + outer_scope_variables)
    })

def parse_variable_reference():
    global syntax_tree
    global outer_scope_variables
    global inner_scope_variables
    global current_block
    global stack
    if stack[1]["type"] != "assignment_operator":
        exit("syntax error")

    eval("syntax_tree " + current_block).append({
        "type": "variable_assignment",
        "expression": Expression(stack, inner_scope_variables + outer_scope_variables)
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
                current_type = node["name"]
            else:
                exit("syntax error")
        elif node["type"] == "variable_name":
            if current_type:
                outer_scope_variables.append({
                    "type": "variable_name",
                    "name": node["name"],
                    "size": 32,
                    "rbp_diff": (len(outer_scope_variables)) * 4
                })
                current_type = ""
            else:
                exit("syntax error")
        else:
            exit("syntax error")

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
                exit("syntax error")
        elif node["type"] == "number":
            arguments.append(node)
            arguments[-1]["argument_rbp_diff"] = -(len(inner_scope_variables) + len(arguments)) * 4
        else:
            exit("syntax error")
    else: # if no ending bracket
        exit("syntax error")
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
                exit("syntax error")
        elif node["type"] == "number":
            arguments.append(node)
        else:
            exit("syntax error")
    else: # if no ending bracket
        exit("syntax error")
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
    eval("syntax_tree " + current_block).append({
        "type": "if",
        "expression": Expression(stack, inner_scope_variables + outer_scope_variables),
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