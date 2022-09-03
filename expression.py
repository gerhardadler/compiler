class Expression:
    def __init__(self, infix_expression):
        self.__infix_expression = infix_expression
        self.postfix_expression = self.create_postfix_from_infix()
        self.postfix_short()


    def create_postfix_from_infix(self):
        # https://en.wikipedia.org/wiki/Shunting_yard_algorithm#The_algorithm_in_detail
        # https://dev.to/quantumsheep/how-calculators-read-mathematical-expression-with-operator-precedence-4n9h
        # https://en.wikipedia.org/wiki/Order_of_operations#Programming_languages
        output = []
        operators = []
        for token in self.__infix_expression:
            if "operator" in token["type"]: # if token is operator
                for operator in reversed(operators):
                    if (token["associativity"] == "right_to_left") and (token["precedence"] > operator["precedence"]):
                        output.append(operators.pop(-1))
                    elif (token["precedence"] >= operator["precedence"]):
                        output.append(operators.pop(-1))
                    else:
                        break
                operators.append(token)
            elif token == "(":
                operators.append(token)
            elif token == ")":
                for operator in reversed(operators):
                    if operator == "(":
                        operators.pop(-1)
                        break
                    else:
                        output.append(operators.pop(-1))
                else:
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
                if token["type"] in ["arithmetic_operator", "comparison_operator"]:
                    operator = self.postfix_expression[index]
                    left = self.postfix_expression[index - 2]
                    right = self.postfix_expression[index - 1]
                    if left["type"] == "number" and right["type"] == "number":
                        del self.postfix_expression[index - 2:index + 1]
                        self.postfix_expression.insert(index - 2, {
                            "symbol": int(eval(str(left["symbol"]) + operator["symbol"] + str(right["symbol"]))),
                            "type": "number"
                        })
                        break
            else:
                break


    def to_assembly(self):
        self.postfix_short()
        data = []
        bss = []
        text = []
        # Short self.postfix_expression
        while True: # While self.postfix_expression keeps getting updated by for loop
            for index, token in enumerate(self.postfix_expression):
                if token in ["+", "-", "*", "/"]:
                    operator = self.postfix_expression[index]
                    right = str(self.postfix_expression[index - 1])
                    left = str(self.postfix_expression[index - 2])
                    if is_str_float(left) and is_str_float(right):
                        del self.postfix_expression[index - 2:index + 1]
                        self.postfix_expression.insert(index - 2, eval(left + operator + right))
                        print(self.postfix_expression)
                        break
            else:
                break
        # self.postfix_expression to assembly
        unused_registers = ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]
        while True: # While there still are operators in self.postfix_expression
            for index, token in enumerate(self.postfix_expression):
                if token in self.operator_lookup:
                    break
            else: # If no more operators
                break
            operator = self.postfix_expression.pop(index)
            right = str(self.postfix_expression.pop(index - 1))
            left = str(self.postfix_expression.pop(index - 2))

            if operator in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="]:
                text.append(f"mov {left}, {right}")
                break

            if left not in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                left_register = unused_registers.pop()
                text.append(f"mov {left_register}, {left}")
                left = left_register
                
            if (not is_str_float(right)) and (right not in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]):
                right_register = unused_registers.pop()
                text.append(f"mov {right_register}, {right}")
                right = right_register
            
            text.append(f"{self.operator_lookup[operator]} {left}, {right}")

            if right in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                unused_registers.append(right)

            self.postfix_expression.insert(index - 2, left)

            return (data, bss, text)