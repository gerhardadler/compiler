from compiler import variable_operation_to_asm
from compiler import registers

class Expression:
    def __init__(self, infix_expression):
        self.infix_expression = infix_expression
        self.postfix_expression = self.create_postfix_from_infix()
        for token in self.postfix_expression:
            print(token["name"], end=" ")
        self.postfix_short()


    def asm_construct(self, instruction, op1, op2):
        return f"{instruction} {op1}, {op2}"


    def create_postfix_from_infix(self):
        # https://en.wikipedia.org/wiki/Shunting_yard_algorithm#The_algorithm_in_detail
        # https://dev.to/quantumsheep/how-calculators-read-mathematical-expression-with-operator-precedence-4n9h
        # https://en.wikipedia.org/wiki/Order_of_operations#Programming_languages
        output = []
        operators = []
        for token in self.infix_expression:
            if "operator" in token["type"]: # if token is operator
                for operator in reversed(operators):
                    if operator["name"] == "(":
                        break
                    elif (token["associativity"] == "right_to_left") and (token["precedence"] > operator["precedence"]):
                        output.append(operators.pop(-1))
                    elif (token["precedence"] >= operator["precedence"]):
                        output.append(operators.pop(-1))
                    else:
                        break
                operators.append(token)
            elif token["name"] == "(":
                operators.append(token)
            elif token["name"] == ")":
                for operator in reversed(operators):
                    if operator["name"] == "(":
                        operators.pop(-1)
                        break
                    else:
                        output.append(operators.pop(-1))
                else: # nobreak
                    print("unmatching parentheses")
            else:
                output.append(token)
        for operator in reversed(operators):
            if operator == "(":
                exit("unmatching parentheses")
            else:
                output.append(operators.pop(-1))
        return output


    def postfix_short(self):
        while True: # While self.postfix_expression keeps getting updated by for loop
            for index, token in enumerate(self.postfix_expression):
                if token["type"] in ["arithmetic_operator", "comparison_operator", "bitwise_operator", "logical_operator"]:
                    operator = self.postfix_expression[index]
                    left = self.postfix_expression[index - 2]
                    right = self.postfix_expression[index - 1]
                    if left["type"] == "number" and right["type"] == "number":
                        del self.postfix_expression[index - 2:index + 1]
                        if operator["name"] == "&&":
                            self.postfix_expression.insert(index - 2, {
                                "name": int(left == 1 and right == 1),
                                "type": "number"
                            })
                        elif operator["name"] == "||":
                            self.postfix_expression.insert(index - 2, {
                                "name": int(left == 1 or right == 1),
                                "type": "number"
                            })
                        else:
                            self.postfix_expression.insert(index - 2, {
                                "name": int(eval(str(left["name"]) + operator["name"] + str(right["name"]))),
                                "type": "number"
                            })
                        break
            else: # nobreak
                break # breaks outer while loop

    def to_asm(self):
        expression = self.postfix_expression
        data = []
        bss = []
        text = []

        unused_registers = [
            registers["rbx"],
            registers["rcx"],
            registers["r11"],
            registers["r12"],
            registers["r13"],
            registers["r14"],
            registers["r15"]
        ]

        # self.postfix_expression to asm
        while True: # While there still are operators in self.postfix_expression
            for index, token in enumerate(expression):
                if token["type"] in ["arithmetic_operator", "assignment_operator"]:
                    break
            else: # nobreak if no more operators
                break
            operator = expression.pop(index)
            right = expression.pop(index - 1)
            left = expression.pop(index - 2)

            print(left)
            print(right)

            if operator["type"] == "assignment_operator":
                if right["type"] == "variable_name":
                    text += variable_operation_to_asm("mov", left, "eax", 2)
                    text += variable_operation_to_asm(operator["asm"], right, "eax", 1)
                else:
                    text += variable_operation_to_asm(operator["asm"], left, right["name"], 1)
                break

            if left["type"] != "register":
                unused_register = unused_registers.pop()
                left_register = {
                    "name": unused_register[max(left.get("size", 0), right.get("size", 0))], # 0 is used as default as not all nodes have a size
                    "type": "register",
                    "full_name": unused_register[64]
                }
                if left["type"] == "variable_name":
                    text += variable_operation_to_asm("mov", left, left_register["name"], 2)
                elif left["type"] == "number":
                    text.append(f"mov {left_register['name']}, {left['name']}")
                else:
                    exit("type not supported in expression code yet")
                left = left_register
            
            if right["type"] == "variable_name":
                unused_register = unused_registers.pop()
                right_register = {
                    "name": unused_register[max(left.get("size", 0), right.get("size", 0))], # 0 is used as default as not all nodes have a size
                    "type": "register",
                    "full_name": unused_register[64]
                }
                text += variable_operation_to_asm(operator["asm"], right, right_register["name"], 2)
                right = right_register
                unused_registers.append(unused_register)

            text.append(f"{operator['asm']} {left['name']}, {right['name']}")

            if right["type"] == "register":
                unused_registers.append(registers[right["full_name"]])

            expression.insert(index - 2, left)

        return {
            "data": data,
            "bss": bss,
            "text": text
        }