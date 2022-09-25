class Expression:
    def __init__(self, infix_expression):
        self.__infix_expression = infix_expression
        self.postfix_expression = self.create_postfix_from_infix()
        for token in self.postfix_expression:
            print(token["symbol"], end=" ")
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
                    if operator["symbol"] == "(":
                        break
                    elif (token["associativity"] == "right_to_left") and (token["precedence"] > operator["precedence"]):
                        output.append(operators.pop(-1))
                    elif (token["precedence"] >= operator["precedence"]):
                        output.append(operators.pop(-1))
                    else:
                        break
                operators.append(token)
            elif token["symbol"] == "(":
                operators.append(token)
            elif token["symbol"] == ")":
                for operator in reversed(operators):
                    if operator["symbol"] == "(":
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
                        if operator["symbol"] == "&&":
                            self.postfix_expression.insert(index - 2, {
                                "symbol": int(left == 1 and right == 1),
                                "type": "number"
                            })
                        elif operator["symbol"] == "||":
                            self.postfix_expression.insert(index - 2, {
                                "symbol": int(left == 1 or right == 1),
                                "type": "number"
                            })
                        else:
                            self.postfix_expression.insert(index - 2, {
                                "symbol": int(eval(str(left["symbol"]) + operator["symbol"] + str(right["symbol"]))),
                                "type": "number"
                            })
                        break
            else: # nobreak
                break # breaks outer while loop


    def to_assembly(self):
        expression = self.postfix_expression
        data = []
        bss = []
        text = []

        # self.postfix_expression to assembly
        unused_registers = ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]
        while True: # While there still are operators in self.postfix_expression
            for index, token in enumerate(expression):
                if token["type"] in ["arithmetic_operator", "assignment_operator"]:
                    break
            else: # nobreak if no more operators
                break
            operator = expression.pop(index)
            right = expression.pop(index - 1)
            left = expression.pop(index - 2)

            if operator["type"] == "assignment_operator":
                text.append(f"mov {left['symbol']}, {right['symbol']}")
                break

            if left["symbol"] not in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                left_register = unused_registers.pop()
                text.append(f"mov {left_register}, {left['symbol']}")
                left["symbol"] = left_register
                
            if (right["type"] != "number") and (right not in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]):
                right_register = unused_registers.pop()
                text.append(f"mov {right_register}, {right['symbol']}")
                right["symbol"] = right_register
            
            text.append(f"{operator['assembly']} {left['symbol']}, {right['symbol']}")

            if right['symbol'] in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                unused_registers.append(right['symbol'])

            expression.insert(index - 2, left)

        return (data, bss, text)