registers = {
    "rax": {"type": "register", "name": "rax", 64: "rax", 32: "eax", 16: "ax", 8: "al"},
    "rbx": {"type": "register", "name": "rbx", 64: "rbx", 32: "ebx", 16: "bx", 8: "bl"},
    "rcx": {"type": "register", "name": "rcx", 64: "rcx", 32: "ecx", 16: "cx", 8: "cl"},
    "rdx": {"type": "register", "name": "rdx", 64: "rdx", 32: "edx", 16: "dx", 8: "dl"},
    "rdi": {"type": "register", "name": "rdi", 64: "rdi", 32: "edi", 16: "di", 8: "dil"},
    "rsi": {"type": "register", "name": "rsi", 64: "rsi", 32: "esi", 16: "si", 8: "sil"},
    "rbp": {"type": "register", "name": "rbp", 64: "rbp", 32: "ebp", 16: "bp", 8: "bpl"}, # THIS REGISTER SHOULD NOT BE USED DUMBASS
    "rsp": {"type": "register", "name": "rsp", 64: "rsp", 32: "esp", 16: "sp", 8: "spl"}, # THIS REGISTER SHOULD NOT BE USED DUMBASS
    "r8": {"type": "register", "name": "r8", 64: "r8", 32: "r8d", 16: "r8w", 8: "r8b"},
    "r9": {"type": "register", "name": "r9", 64: "r9", 32: "r9d", 16: "r9w", 8: "r9b"},
    "r10": {"type": "register", "name": "r10", 64: "r10", 32: "r10d", 16: "r10w", 8: "r10b"},
    "r11": {"type": "register", "name": "r11", 64: "r11", 32: "r11d", 16: "r11w", 8: "r11b"},
    "r12": {"type": "register", "name": "r12", 64: "r12", 32: "r12d", 16: "r12w", 8: "r12b"},
    "r13": {"type": "register", "name": "r13", 64: "r13", 32: "r13d", 16: "r13w", 8: "r13b"},
    "r14": {"type": "register", "name": "r14", 64: "r14", 32: "r14d", 16: "r14w", 8: "r14b"},
    "r15": {"type": "register", "name": "r15", 64: "r15", 32: "r15d", 16: "r15w", 8: "r15b"}
}

def add_asm_line(text, instruction, op1, op2):
    text.append(f"{instruction} {op1}, {op2}")

def apply_rbp_diff(variable):
    return f"{'add' if variable['rbp_diff'] >= 0 else 'sub'} rbp, {abs(variable['rbp_diff'])}"

def unapply_rbp_diff(variable):
    return f"{'sub' if variable['rbp_diff'] >= 0 else 'add'} rbp, {abs(variable['rbp_diff'])}"

def get_variable_rbp_reference(variable): # returns a string depending on if variable has "address_of"=True
    if variable["address_of"] is True:
        return "rbp"
    else:
        return f"{variable['size_specifier']} [rbp]"

def create_asm(instruction, op1, op2):
    output = []
    if op1["type"] == "variable_name":
        if op2["type"] == "variable_name":
            if op2["address_of"] == False:
                output.append(apply_rbp_diff(op2))
                if op1["size"] == 64 and op2["size"] == 32: # https://stackoverflow.com/questions/11177137/why-do-x86-64-instructions-on-32-bit-registers-zero-the-upper-part-of-the-full-6
                    register = registers["rax"][32]
                    output.append(f"mov {register}, {op2['size_specifier']} [rbp]")
                    register = registers["rax"][64]
                elif op1["size"] > op2["size"]:
                    register = registers["rax"][op1['size']]
                    output.append(f"movzx {register}, {op2['size_specifier']} [rbp]")
                else:
                    register = registers["rax"][op1['size']]
                    output.append(f"mov {register}, {op1['size_specifier']} [rbp]")
                output.append(unapply_rbp_diff(op2))
                op2 = register
            else:
                if op1["size"] != 64:
                    exit("references need a size of 64 bits")
                output.append(apply_rbp_diff(op2))
                op2 = registers["rbp"][op1["size"]]
                output.append(unapply_rbp_diff(op2))
        elif op2["type"] == "function_reference":
            for argument in op2["arguments"]:
                output += argument["expression"].to_asm()["text"]
            add_asm_line(output, "sub", "rsp", abs(op2['function_rsp_offset']))
            output.append("call " + op2["name"])
            add_asm_line(output, "add", "rsp", abs(op2['function_rsp_offset']))
            op2 = op2 = registers["rax"][op1["size"]]
        elif op2["type"] == "register":
            op2 = op2[op1["size"]]
        elif op2["type"] == "number":
            op2 = op2["name"] # maybe add check if number is too big
        else:
            exit("not supported type")
        output.append(apply_rbp_diff(op1))
        output.append(f"{instruction} {get_variable_rbp_reference(op1)}, {op2}")
        output.append(unapply_rbp_diff(op1))
    elif op1["type"] == "register":
        if op2["type"] == "variable_name":
            if op2["address_of"] == False:
                output.append(apply_rbp_diff(op2))
                if op2["size"] == 32:
                    register = registers["rax"][32]
                    output.append(f"mov {register}, {op2['size_specifier']} [rbp]")
                elif 64 > op2["size"]: # https://stackoverflow.com/questions/11177137/why-do-x86-64-instructions-on-32-bit-registers-zero-the-upper-part-of-the-full-6
                    register = registers["rax"][64]
                    output.append(f"movzx {register}, {op2['size_specifier']} [rbp]")
                else:
                    register = registers["rax"][64]
                    output.append(f"mov {register}, qword [rbp]")
                output.append(unapply_rbp_diff(op2))
                output.append(f"{instruction} {op1[64]}, {registers['rax'][64]}")
            else:
                output.append(apply_rbp_diff(op2))
                output.append(f"{instruction} {op1[64]}, {registers['rbp'][64]}")
                output.append(unapply_rbp_diff(op2))
        elif op2["type"] == "function_reference":
            for argument in op2["arguments"]:
                output += argument["expression"].to_asm()["text"]
            add_asm_line(output, "sub", "rsp", abs(op2['function_rsp_offset']))
            output.append("call " + op2["name"])
            add_asm_line(output, "add", "rsp", abs(op2['function_rsp_offset']))
            op2 = op2 = registers["rax"][op1["size"]]
        elif op2["type"] == "register":
            output.append(f"{instruction} {op1[64]}, {op2[64]}")
        elif op2["type"] == "number":
            output.append(f"{instruction} {op1[64]}, {op2['name']}")
        else:
            exit("not supported type")
    else:
        exit("not supported type")
    print(output)
    return output

# def variable_operation_to_asm(instruction, variable, op, variable_spot, rbp_offset = 0):
#         output = []
#         if variable["rbp_diff"] >= 0:
#             add_asm_line(output, "add", "rbp", variable['rbp_diff'] + rbp_offset)
#             if variable_spot == 1:
#                 add_asm_line(output, instruction, get_variable_rbp_reference(variable), op)
#             else:
#                 add_asm_line(output, instruction, op, get_variable_rbp_reference(variable))
#             add_asm_line(output, "sub", "rbp", variable['rbp_diff'] + rbp_offset)
#         else:
#             add_asm_line(output, "sub", "rbp", variable['rbp_diff'] + rbp_offset)
#             if variable_spot == 1:
#                 add_asm_line(output, instruction, get_variable_rbp_reference(variable), op)
#             else:
#                 add_asm_line(output, instruction, op, get_variable_rbp_reference(variable))
#             add_asm_line(output, "add", "rbp", variable['rbp_diff'] + rbp_offset)
#         return output

def compiler(syntax_tree, header=True):
    data = []
    bss = []
    text = []
    if header == True:
        text += ["section .text", "global _start", "_start:", "call main", "mov rax, 60", "mov rdi, 0", "syscall"]

    for node in syntax_tree:
        if node["type"] == "variable_declaration":
            expression_asm = node["expression"].to_asm()
            text += expression_asm["text"]
            text += create_asm(node["assignment_operator"]["asm"], node["variable"], expression_asm["value"])
        elif node["type"] == "variable_assignment":
            expression_asm = node["expression"].to_asm()
            text += expression_asm["text"]
            text += create_asm(node["assignment_operator"]["asm"], node["variable"], expression_asm["value"])
        elif node["type"] == "function_declaration":
            text.append(node["name"] + ":")
            text.append("push rbp")
            add_asm_line(text, "mov", "rbp", "rsp")
            text += compiler(node["body"], header=False)["text"]

            add_asm_line(text, "mov", "rax", "0")
            text.append(f"{node['name']}_ret:") # label for returning
            add_asm_line(text, "mov", "rsp", "rbp")
            text.append("pop rbp")
            text.append("ret")
        elif node["type"] == "function_reference":
            for argument in node["arguments"]:
                argument_asm = argument["expression"].to_asm()
                text += argument_asm["text"]
                text += create_asm("mov", argument["variable"], argument_asm["value"])
            add_asm_line(text, "sub", "rsp", abs(node['function_rsp_offset']))
            text.append("call " + node["name"])
            add_asm_line(text, "add", "rsp", abs(node['function_rsp_offset']))
        elif node["type"] == "return":
            return_asm = node["expression"].to_asm()
            text += return_asm["text"]
            text += create_asm("mov", registers["rax"], return_asm["value"])
            text.append(f"jmp {node['current_function_name']}_ret")
        elif node["type"] == "syscall": # https://stackoverflow.com/a/2538212/12834165
            for argument in node["arguments"]:
                argument_asm = argument["expression"].to_asm()
                text += argument_asm["text"]
                text += create_asm("mov", argument["syscall_register"], argument_asm["value"])
            # syscall_registers = [
            #     registers["rax"],
            #     registers["rdi"],
            #     registers["rsi"],
            #     registers["rdx"],
            #     registers["r10"],
            #     registers["r9"],
            #     registers["r8"]
            # ]
            # for register, argument in list(zip(syscall_registers, node["arguments"])):
            #     if argument["type"] == "variable_name":
            #         push_rbp_diff = 16
            #         if argument["rbp_diff"] >= 0:
            #             add_asm_line(text, "add", "rbp", argument['rbp_diff'] + push_rbp_diff)
            #             add_asm_line(text, "mov", register[64], get_variable_rbp_reference(argument)) # issues with movzx
            #             add_asm_line(text, "sub", "rbp", argument['rbp_diff'] + push_rbp_diff)
            #         else:
            #             add_asm_line(text, "sub", "rbp", abs(argument['rbp_diff'] + push_rbp_diff))
            #             add_asm_line(text, "movzx", register[64], get_variable_rbp_reference(argument))
            #             add_asm_line(text, "add", "rbp", abs(argument['rbp_diff'] + push_rbp_diff))
            #     elif argument["type"] == "number":
            #         add_asm_line(text, "mov", register[64], argument["name"])
            text.append("syscall")
    
    return {
        "data": data,
        "bss": bss,
        "text": text
    }