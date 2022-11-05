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

def add_asm_line(text, instruction, op1, op2):
    text.append(f"{instruction} {op1}, {op2}")

# def apply_rbp_diff(variable):
#     return f"{'add' if variable['rbp_diff'] >= 0 else 'sub'} rbp, {abs(variable['rbp_diff'])}"

# def unapply_rbp_diff(variable):
#     return f"{'add' if variable['rbp_diff'] >= 0 else 'sub'} rbp, {abs(variable['rbp_diff'])}"


# def add_instruction(text, instruction, op1, op2):
#     if op1["type"] == "variable_name":
#         if op2["type"] == "variable_name":
#             text.append(apply_rbp_diff(op2))
#             text.append(f"mov {registers['rax'][op1['size']]}, {op1['size_specifier']} [rbp]")
#             text.append(unapply_rbp_diff(op2))
#         else

#     else:
#     text.append(f"{instruction} {op1}, {op2}")

def get_variable_rbp_reference(variable): # returns a string depending on if variable has "address_of"=True
    if variable["address_of"] is True:
        return "rbp"
    else:
        return f"{variable['size_specifier']} [rbp]"

def variable_operation_to_asm(instruction, variable, op, variable_spot, rbp_offset = 0):
        output = []
        if variable["rbp_diff"] >= 0:
            add_asm_line(output, "add", "rbp", variable['rbp_diff'] + rbp_offset)
            if variable_spot == 1:
                add_asm_line(output, instruction, get_variable_rbp_reference(variable), op)
            else:
                add_asm_line(output, instruction, op, get_variable_rbp_reference(variable))
            add_asm_line(output, "sub", "rbp", variable['rbp_diff'] + rbp_offset)
        else:
            add_asm_line(output, "sub", "rbp", variable['rbp_diff'] + rbp_offset)
            if variable_spot == 1:
                add_asm_line(output, instruction, get_variable_rbp_reference(variable), op)
            else:
                add_asm_line(output, instruction, op, get_variable_rbp_reference(variable))
            add_asm_line(output, "add", "rbp", variable['rbp_diff'] + rbp_offset)
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
            add_asm_line(text, "mov", "rbp", "rsp")
            text += compiler(node["body"], header=False)["text"]

            add_asm_line(text, "mov", "rsp", "rbp")
            text.append("pop rbp")
            text.append("ret")
        elif node["type"] == "function_name":
            for argument in node["arguments"]:
                if argument["type"] == "variable_name":
                    rax_register = registers["rax"][argument["size"]]
                    text += variable_operation_to_asm("mov", argument, rax_register, 2)
                    add_asm_line(text, "sub", "rbp", abs(argument['argument_rbp_diff']))
                    add_asm_line(text, "mov", f"{argument['parameter_size_specifier']} [rbp]", rax_register)
                    add_asm_line(text, "add", "rbp", abs(argument['argument_rbp_diff']))
                elif argument["type"] == "number":
                    add_asm_line(text, "sub", "rbp", abs(argument['argument_rbp_diff']))
                    add_asm_line(text, "mov", f"{argument['parameter_size_specifier']} [rbp]", argument['name'])
                    add_asm_line(text, "add", "rbp", abs(argument['argument_rbp_diff']))
            add_asm_line(text, "sub", "rsp", abs(argument['argument_rbp_diff']))
            text.append("call " + node["name"])
            add_asm_line(text, "add", "rsp", abs(argument['argument_rbp_diff']))
        elif node["type"] == "syscall": # https://stackoverflow.com/a/2538212/12834165
            text.append("push rcx")
            text.append("push r11")
            syscall_registers = [
                registers["rax"],
                registers["rdi"],
                registers["rsi"],
                registers["rdx"],
                registers["r10"],
                registers["r9"],
                registers["r8"]
            ]
            for register, argument in list(zip(syscall_registers, node["arguments"])):
                if argument["type"] == "variable_name":
                    push_rbp_diff = 16
                    if argument["rbp_diff"] >= 0:
                        add_asm_line(text, "add", "rbp", argument['rbp_diff'] + push_rbp_diff)
                        add_asm_line(text, "mov", register[64], get_variable_rbp_reference(argument)) # issues with movzx
                        add_asm_line(text, "sub", "rbp", argument['rbp_diff'] + push_rbp_diff)
                    else:
                        add_asm_line(text, "sub", "rbp", abs(argument['rbp_diff'] + push_rbp_diff))
                        add_asm_line(text, "movzx", register[64], get_variable_rbp_reference(argument))
                        add_asm_line(text, "add", "rbp", abs(argument['rbp_diff'] + push_rbp_diff))
                elif argument["type"] == "number":
                    add_asm_line(text, "mov", register[64], argument["name"])
            text.append("syscall")
            text.append("pop r11")
            text.append("pop rcx")
    
    return {
        "data": data,
        "bss": bss,
        "text": text
    }