class Variable:
    def __init__(self, variable_type, variable_name, scope_rbp_diff):
        self.type = "variable_name"
        self.name = variable_name["name"]
        self.variable_type = variable_type["name"]
        self.size = variable_type["size"]
        self.size_specifier == self.size_to_specifier
        if scope_rbp_diff >= 0:
            self.rbp_diff = scope_rbp_diff
        else:
            self.rbp_diff = scope_rbp_diff - variable_type["size"] // 8
    
    def size_to_specifier(self):
        if self.size == 8:
            return "byte"
        if self.size == 16:
            return "word"
        if self.size == 32:
            return "dword"
        if self.size == 64:
            return "qword"
        # if nothing matches
        raise Exception("Invalid size")

    def operation_to_assembly(self, instruction, op, variable_spot, rbp_offset = 0):
        output = []
        if self.rbp_diff >= 0:
            output.append(f"add rbp, {self.rbp_diff + rbp_offset}")
            if variable_spot == 1:
                output.append(f"{instruction} {self.size_specifier} [rbp], {op}")
            else:
                output.append(f"{instruction} {op}, {self.size_specifier} [rbp]")
            output.append(f"sub rbp, {self.rbp_diff + rbp_offset}")
        else:
            output.append(f"sub rbp, {abs(self.rbp_diff) + rbp_offset}")
            if variable_spot == 1:
                output.append(f"{instruction} {self.size_specifier} [rbp], {op}")
            else:
                output.append(f"{instruction} {op}, {self.size_specifier} [rbp]")
            output.append(f"add rbp, {abs(self.rbp_diff) + rbp_offset}")
        return output