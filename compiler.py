def compiler(syntax_tree, header=True):
    data = []
    bss = []
    text = []
    if header == True:
        text += ["section .text", "global _start", "_start:", "call main", "mov rax, 60", "mov rdi, 0", "syscall"]

    for node in syntax_tree:
        if node["type"] == "variable_declaration":
            variable_name = node['expression'].postfix_expression[0]['symbol']
            value = node['expression'].postfix_expression[1]['symbol']
            # TODO: not make it only 32 bit
            text.append(f"mov {variable_name}, {value}")
        elif node["type"] == "variable_assignment":
            text += node["expression"].to_assembly()["text"]
        elif node["type"] == "function":
            text.append(node["name"] + ":")
            text.append("push rbp")
            text.append("mov rbp, rsp")
            text += compiler(node["body"], header=False)["text"]

            text.append("mov rsp, rbp")
            text.append("pop rbp")
            text.append("ret")
        elif node["type"] == "function_name":
            for argument in node["arguments"]:
                text.append("sub rsp, 4")
                text.append(f"mov rsp, {argument}")
            text.append("call " + node["name"])
            for argument in node["arguments"]:
                text.append("add rsp, 4")
    
    return {
        "data": data,
        "bss": bss,
        "text": text
    }