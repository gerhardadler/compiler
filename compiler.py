registers = {
    "rax": {"type": "register", 64: "rax", 32: "eax", 16: "ax", 8: "al"},
    "rbx": {"type": "register", 64: "rbx", 32: "ebx", 16: "bx", 8: "bl"},
    "rcx": {"type": "register", 64: "rcx", 32: "ecx", 16: "cx", 8: "cl"},
    "rdx": {"type": "register", 64: "rdx", 32: "edx", 16: "dx", 8: "dl"},
    "rdi": {"type": "register", 64: "rdi", 32: "edi", 16: "di", 8: "dil"},
    "rsi": {"type": "register", 64: "rsi", 32: "esi", 16: "si", 8: "sil"},
    "rbp": {"type": "register", 64: "rbp", 32: "ebp", 16: "bp", 8: "bpl"}, # THIS REGISTER SHOULD NOT BE USED DUMBASS
    "rsp": {"type": "register", 64: "rsp", 32: "esp", 16: "sp", 8: "spl"}, # THIS REGISTER SHOULD NOT BE USED DUMBASS
    "r8": {"type": "register", 64: "r8", 32: "r8d", 16: "r8w", 8: "r8b"},
    "r9": {"type": "register", 64: "r9", 32: "r9d", 16: "r9w", 8: "r9b"},
    "r10": {"type": "register", 64: "r10", 32: "r10d", 16: "r10w", 8: "r10b"},
    "r11": {"type": "register", 64: "r11", 32: "r11d", 16: "r11w", 8: "r11b"},
    "r12": {"type": "register", 64: "r12", 32: "r12d", 16: "r12w", 8: "r12b"},
    "r13": {"type": "register", 64: "r13", 32: "r13d", 16: "r13w", 8: "r13b"},
    "r14": {"type": "register", 64: "r14", 32: "r14d", 16: "r14w", 8: "r14b"},
    "r15": {"type": "register", 64: "r15", 32: "r15d", 16: "r15w", 8: "r15b"}
}

def variable_operation_to_asm(instruction, variable, op, variable_spot, rbp_offset = 0):
        output = []
        if variable["rbp_diff"] >= 0:
            output.append(f"add rbp, {variable['rbp_diff'] + rbp_offset}")
            if variable_spot == 1:
                output.append(f"{instruction} {variable['size_specifier']} [rbp], {op}")
            else:
                output.append(f"{instruction} {op}, {variable['size_specifier']} [rbp]")
            output.append(f"sub rbp, {variable['rbp_diff'] + rbp_offset}")
        else:
            output.append(f"sub rbp, {abs(variable['rbp_diff']) + rbp_offset}")
            if variable_spot == 1:
                output.append(f"{instruction} {variable['size_specifier']} [rbp], {op}")
            else:
                output.append(f"{instruction} {op}, {variable['size_specifier']} [rbp]")
            output.append(f"add rbp, {abs(variable['rbp_diff']) + rbp_offset}")
        return output

def compiler(syntax_tree, header=True):
    data = []
    bss = []
    text = []
    if header == True:
        text += ["section .text", "global _start", "_start:", "call main", "mov rax, 60", "mov rdi, 0", "syscall"]

    for node in syntax_tree:
        if node["type"] == "variable_declaration":
            text += node["expression"].to_asm()["text"]
        elif node["type"] == "variable_assignment":
            text += node["expression"].to_asm()["text"]
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
                if argument["type"] == "variable_name":
                    rax_register = registers["rax"][argument["size"]]
                    text += variable_operation_to_asm("mov", argument, rax_register, 2)
                    text.append(f"sub rbp, {abs(argument['argument_rbp_diff'])}")
                    text.append(f"mov {argument['parameter_size_specifier']} [rbp], {rax_register}")
                    text.append(f"add rbp, {abs(argument['argument_rbp_diff'])}")
                elif argument["type"] == "number":
                    text.append(f"sub rbp, {abs(argument['argument_rbp_diff'])}")
                    text.append(f"mov {argument['parameter_size_specifier']} [rbp], {argument['name']}")
                    text.append(f"add rbp, {abs(argument['argument_rbp_diff'])}")
            text.append(f"sub rsp, {abs(argument['argument_rbp_diff'])}")
            text.append("call " + node["name"])
            text.append(f"add rsp, {abs(argument['argument_rbp_diff'])}")
        elif node["type"] == "syscall": # https://stackoverflow.com/a/2538212/12834165
            text.append("push rcx")
            text.append("push r11")
            syscall_registers = ["rax", "rdi", "rsi", "rdx", "r10", "r9", "r8"]
            for argument in list(zip(syscall_registers, node["arguments"])):
                if argument[1]["type"] == "variable_name":
                    push_rbp_diff = 16
                    if argument[1]["rbp_diff"] >= 0:
                        text.append(f"add rbp, {argument[1]['rbp_diff'] + push_rbp_diff}")
                        text.append(f"mov {argument[0]}, rbp")
                        text.append(f"sub rbp, {argument[1]['rbp_diff'] + push_rbp_diff}")
                    else:
                        text.append(f"sub rbp, {abs(argument[1]['rbp_diff'])}")
                        text.append(f"mov {argument[0]}, rbp")
                        text.append(f"add rbp, {abs(argument[1]['rbp_diff'])}")
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