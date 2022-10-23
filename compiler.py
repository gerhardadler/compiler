def compiler(syntax_tree, header=True):
    data = []
    bss = []
    text = []
    if header == True:
        text += ["section .text", "global _start", "_start:", "call main", "mov rax, 60", "mov rdi, 0", "syscall"]

    for node in syntax_tree:
        if node["type"] == "variable_declaration":
            variable_name = node['expression'].postfix_expression[0]['name']
            value = node['expression'].postfix_expression[1]['name']
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
        elif node["type"] == "syscall": # https://stackoverflow.com/a/2538212/12834165
            text.append("push rcx")
            text.append("push r11")
            push_rbp_diff = 16 
            syscall_registers = ["rax", "rdi", "rsi", "rdx", "r10", "r9", "r8"]
            for argument in list(zip(syscall_registers, node["arguments"])):
                if argument[1]["type"] == "variable_name":
                    if argument[1]["rbp_diff"] > 0:
                        text.append(f"add rbp, {argument[1]['rbp_diff'] + push_rbp_diff}")
                        text.append(f"mov {argument[0]}, rbp")
                        text.append(f"sub rbp, {abs(argument[1]['rbp_diff']) + push_rbp_diff}")
                    else:
                        text.append(f"sub rbp, {abs(argument[1]['rbp_diff']) + push_rbp_diff}")
                        text.append(f"mov {argument[0]}, rbp")
                        text.append(f"add rbp, {abs(argument[1]['rbp_diff']) + push_rbp_diff}")
                elif argument[1]["type"] == "number":
                    text.append(f"mov {argument[0]}, {argument[1]['name']}")
            text.append("syscall")
            text.append("pop r11")
            text.append("pop rcx")
    
    return {
        "data": data,
        "bss": bss,
        "text": text
    }