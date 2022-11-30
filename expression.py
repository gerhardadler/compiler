from compiler import create_asm
from compiler import registers

class Expression:
    def __init__(self, infix_expression):
        self.postfix_expression = self.create_postfix(infix_expression)
        for token in self.postfix_expression:
            print(token["name"], end=" ")
        self.postfix_short()

    def create_postfix(self, infix_expression):
        # https://en.wikipedia.org/wiki/Shunting_yard_algorithm#The_algorithm_in_detail
        # https://dev.to/quantumsheep/how-calculators-read-mathematical-expression-with-operator-precedence-4n9h
        # https://en.wikipedia.org/wiki/Order_of_operations#Programming_languages
        output = []
        operators = []
        for token in infix_expression:
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
        expression = self.postfix_expression.copy()
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
        while len(expression) > 1: # While there still are operators in self.postfix_expression
            for index, token in enumerate(expression):
                if token["type"] in ["arithmetic_operator", "comparison_operator"]:
                    break
            else:
                exit("shocker innit")
            operator = expression.pop(index)
            right = expression.pop(index - 1)
            left = expression.pop(index - 2)

            # text += create_asm(operator["asm"], left, right)
            # if operator["type"] == "assignment_operator":
            #     text += create_asm(operator["asm"], left, right)
            #     # print(text)
            #     break

            if left["type"] != "register":
                # unused_register = unused_registers.pop()
                left_register = unused_registers.pop()
                text += create_asm("mov", left_register, left)
                left = left_register
            
            # if right["type"] == "variable_name":
            #     # unused_register = unused_registers.pop()
            #     right_register = unused_registers.pop()
            #     text += create_asm(operator["asm"], right_register["name"], right)
            #     right = right_register
            #     unused_registers.append(right_register)

            text += create_asm(operator["asm"], left, right)
            # text.append(f"{operator['asm']} {left['name']}, {right['name']}")

            # if right["type"] == "register":
            #     unused_registers.append(registers[right["full_name"]])

            expression.insert(index - 2, left)
        
        # in case expression has a length of 1
        try:
            left
        except NameError: # left isn't defined
            left = expression.pop()
            if left["type"] == "variable_name":
                left_register = unused_registers.pop()
                text += create_asm("mov", left_register, left)
                left = left_register

        return {
            "data": data,
            "bss": bss,
            "text": text,
            "value": left
        }