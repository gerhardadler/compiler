from expression import Expression

def parser(tokens):
    syntax_tree = []
    current_scope = "syntax_tree"
    stack = []
    for token in tokens:
        if token["type"] in ["seperator", "curly_bracket"]:
            if token["symbol"] == "}":
                current_scope = current_scope[0:-12]
            elif stack[0]["type"] == "type_declaration":
                if stack[1]["type"] != "variable_name":
                    exit("syntax error")
                if stack[2]["type"] != "assignment_operator":
                    exit("syntax error")

                eval(current_scope).append({
                    "type": "variable_declaration",
                    "variable_type": stack.pop(0)["symbol"],
                    "expression": Expression(stack)
                })
            elif stack[0]["type"] == "variable_name":
                if stack[1]["type"] != "assignment_operator":
                    exit("syntax error")

                eval(current_scope).append({
                    "type": "variable_assignment",
                    "expression": Expression(stack)
                })
            elif stack[0]["symbol"] == "if":
                eval(current_scope).append({
                    "type": "if",
                    "expression": Expression(stack),
                    "body": []
                })
                current_scope += '[-1]["body"]'
            stack = []
        else:
            stack.append(token)
    return syntax_tree