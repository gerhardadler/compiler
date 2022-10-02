from expression import Expression

def parser(tokens):
    syntax_tree = []
    variable_table = []
    current_scope = ""
    stack = []
    for token in tokens:
        if token["type"] in ["semicolon", "curly_bracket"]:
            if token["symbol"] == "}":
                current_scope = current_scope[0:-12]
            elif stack[0]["type"] == "type_declaration":
                if stack[1]["type"] != "variable_name":
                    exit("syntax error")
                if stack[2]["symbol"] != "=":
                    exit("syntax error")
                if stack[3]["type"] != "number":
                    exit("syntax_error")

                variable_type = stack.pop(0)["symbol"]
                eval("syntax_tree " + current_scope).append({
                    "type": "variable_declaration",
                    "variable_type": variable_type,
                    "expression": Expression(stack)
                })

                eval("variable_table " + current_scope).append({
                    "variable_type": variable_type,
                    "name": stack[0],
                })
            elif stack[0]["type"] == "variable_name":
                if stack[1]["type"] != "assignment_operator":
                    exit("syntax error")
                
                for var in eval("variable_table " + current_scope):
                    if stack[0] == var.get("name"):
                        break
                else: # nobreak
                    exit("wrong scope")

                eval("syntax_tree " + current_scope).append({
                    "type": "variable_assignment",
                    "expression": Expression(stack)
                })
            elif stack[0]["type"] == "function":
                eval("syntax_tree " + current_scope).append({
                    "type": stack.pop(0)["type"],
                    "name": stack.pop(0)["symbol"],
                    # "variables": make function work with variables,
                    "body": []
                })
                eval("variable_table " + current_scope).append({
                    "body": []
                })
                current_scope += '[-1]["body"]'
            elif stack[0]["type"] == "if":
                eval("syntax_tree " + current_scope).append({
                    "type": "if",
                    "expression": Expression(stack),
                    "body": []
                })
                eval("variable_table " + current_scope).append({
                    "body": []
                })
                current_scope += '[-1]["body"]'
            stack = []
        else:
            stack.append(token)
    return syntax_tree