def compiler(syntax_tree):
    data = []
    bss = []
    text = []
    for node in syntax_tree:
        if node["type"] == "variable_declaration":
            variable_name = node['expression'].postfix_expression[0]['symbol']
            value = node['expression'].postfix_expression[1]['symbol']
            # TODO: not make it only dd.
            data.append(f"{variable_name} dd {value}")
        elif node["type"] == "variable_assignment":
            text.append(node["expression"].to_assembly()["text"])
        elif node["type"] == "function":
            text.append(node["name"] + ":")
            text.append("push rbp")
            text.append("mov rbp, rsp")
            text.append(compiler(node["body"])["text"])

            text.append("mov rsp, rbp")
            text.append("pop rbp")
            text.append("ret")
    
    return {
        "data": data,
        "bss": bss,
        "text": text
    }