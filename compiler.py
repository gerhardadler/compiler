def compiler(syntax_tree):
    scope_variables = []
    data = []
    bss = []
    text = []
    for node in syntax_tree:
        if node["type"] == "variable_declaration":
            variable_name = node['expression'].postfix_expression[0]['symbol']
            value = node['expression'].postfix_expression[1]['symbol']
            # TODO: not make it only 32 bit
            scope_variables.append({
                "name": variable_name,
                "value": value,
                "size": 32,
                "rbp_diff": (len(scope_variables) + 1) * 4
            })
            text.append(f"mov [rpb-{scope_variables[-1]['rbp_diff']}], {value}")
        elif node["type"] == "variable_assignment":
            text += node["expression"].to_assembly()["text"]
        elif node["type"] == "function":
            text.append(node["name"] + ":")
            text.append("push rbp")
            text.append("mov rbp, rsp")
            text += compiler(node["body"])["text"]

            text.append("mov rsp, rbp")
            text.append("pop rbp")
            text.append("ret")
    
    return {
        "data": data,
        "bss": bss,
        "text": text
    }