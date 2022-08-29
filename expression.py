from is_str_float import is_str_float

class Expression:
    def __init__(self, infix_expression):
        operators = [
            {"symbol": "*", "precedence": 2,  "associativity": "left_to_right", "assembly": "mul", "assignment": False},
            {"symbol": "/", "precedence": 2,  "associativity": "left_to_right", "assembly": "div", "assignment": False},
            {"symbol": "+", "precedence": 3,  "associativity": "left_to_right", "assembly": "add", "assignment": False},
            {"symbol": "-", "precedence": 3,  "associativity": "left_to_right", "assembly": "sub", "assignment": False},
            {"symbol": "=", "precedence": 12, "associativity": "right_to_left", "assembly": "mov", "assignment": True}

        ]
        self.precedence = {
            "()": 0, "[]": 0,
            "!": 1, "~": 1, "-u": 1, "+u": 1, "++": 1, "--": 1,
            "*": 2, "/": 2, "%": 2,
            "+": 3, "-": 3,
            "<<": 4, ">>": 4,
            "<": 5, ">": 5, "<=": 5, ">=": 5,
            "==": 6, "!=": 6,
            "&": 7,
            "^": 8,
            "|": 9,
            "&&": 10,
            "||": 11,
            "=": 12, "+=": 12, "-=": 12, "*=": 12, "/=": 12, "%=": 12, "&=": 12, "|=": 12, "^=": 12, "<<=": 12, ">>=": 12
        }
        self.associativity = {
            # The other operators are all "left to right"
            1: "right_to_left",
            12: "right_to_left"
        }

        self.assignment_operator_lookup = {
            "=": "mov",
            "+=": "add",
            "-=": "sub",
            "*=": "mul",
            "/=": "div"
        }

        self.code_operator_lookup = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div"
        }

        self.infix_expression = infix_expression
        self.postfix_expression = self.create_postfix_from_infix()

    def create_postfix_from_infix(self):
        # https://en.wikipedia.org/wiki/Shunting_yard_algorithm#The_algorithm_in_detail
        # https://dev.to/quantumsheep/how-calculators-read-mathematical-expression-with-code_operator-precedence-4n9h
        # https://en.wikipedia.org/wiki/Order_of_operations#Programming_languages
        output = []
        code_operators = []
        for token in self.infix_expression:
            if token in self.precedence: # if token is code_operator
                for code_operator in reversed(code_operators):
                    if code_operator not in self.precedence:
                        break
                    if (self.associativity.get(self.precedence[token]) == "right_to_left") and (self.precedence[token] > self.precedence[code_operator]):
                        output.append(code_operators.pop(-1))
                    elif (self.precedence[token] >= self.precedence[code_operator]):
                        output.append(code_operators.pop(-1))
                    else:
                        break
                code_operators.append(token)
            elif token == "(":
                code_operators.append(token)
            elif token == ")":
                for code_operator in reversed(code_operators):
                    if code_operator == "(":
                        code_operators.pop(-1)
                        break
                    else:
                        output.append(code_operators.pop(-1))
                else:
                    print("unmatching parentheses")
            else:
                output.append(token)
        for code_operator in reversed(code_operators):
            if code_operator == "(":
                print("unmatching parentheses")
            else:
                output.append(code_operators.pop(-1))
        return output


    def short(self):
        while True: # While self.postfix_expression keeps getting updated by for loop
            for index, token in enumerate(self.postfix_expression):
                if token in ["+", "-", "*", "/"]:
                    code_operator = self.postfix_expression[index]
                    right = str(self.postfix_expression[index - 1])
                    left = str(self.postfix_expression[index - 2])
                    if is_str_float(left) and is_str_float(right):
                        del self.postfix_expression[index - 2:index + 1]
                        self.postfix_expression.insert(index - 2, eval(left + code_operator + right))
                        print(self.postfix_expression)
                        break
            else:
                break


    def to_assembly(self):
        self.short()
        data = []
        bss = []
        text = []
        # Short self.postfix_expression
        while True: # While self.postfix_expression keeps getting updated by for loop
            for index, token in enumerate(self.postfix_expression):
                if token in ["+", "-", "*", "/"]:
                    code_operator = self.postfix_expression[index]
                    right = str(self.postfix_expression[index - 1])
                    left = str(self.postfix_expression[index - 2])
                    if is_str_float(left) and is_str_float(right):
                        del self.postfix_expression[index - 2:index + 1]
                        self.postfix_expression.insert(index - 2, eval(left + code_operator + right))
                        print(self.postfix_expression)
                        break
            else:
                break
        # self.postfix_expression to assembly
        unused_registers = ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]
        while True: # While there still are operators in self.postfix_expression
            for index, token in enumerate(self.postfix_expression):
                if token in self.code_operator_lookup:
                    break
            else: # If no more operators
                break
            code_operator = self.postfix_expression.pop(index)
            right = str(self.postfix_expression.pop(index - 1))
            left = str(self.postfix_expression.pop(index - 2))

            if code_operator in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="]:
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
            
            text.append(f"{self.code_operator_lookup[code_operator]} {left}, {right}")

            if right in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                unused_registers.append(right)

            self.postfix_expression.insert(index - 2, left)

            return (data, bss, text)