code = """
uint x = 3

x = 2

if x == 3 {
    x = 4
}
"""

def str_is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def expression_to_rpn(expression):
    # https://en.wikipedia.org/wiki/Shunting_yard_algorithm#The_algorithm_in_detail
    # https://dev.to/quantumsheep/how-calculators-read-mathematical-expression-with-code_operator-precedence-4n9h
    # https://en.wikipedia.org/wiki/Order_of_operations#Programming_languages
    precedence = {
        "()": 0, "[]": 0,
        "!": 1, "~": 1, "-u": 1, "+u": 1, "++": 1, "--": 1,
        "*": 2, "/": 1, "%": 2,
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
    associativity = {
        # The other operators are all "left to right"
        1: "right_to_left",
        12: "right_to_left"
    }
    output = []
    code_operators = []
    for token in expression:
        if token in precedence: # if token is code_operator
            for code_operator in reversed(code_operators):
                if code_operator not in precedence:
                    break
                if (associativity.get(precedence[token]) == "right_to_left") and (precedence[token] > precedence[code_operator]):
                    output.append(code_operators.pop(-1))
                elif (precedence[token] >= precedence[code_operator]):
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

syntax_tree = []
current_scope = "syntax_tree"

for line_number, line in enumerate(code.split("\n")):
    line = line.split()
    if len(line) == 0:
        continue
    elif line[0] == "}":
        current_scope = current_scope[0:-12]
        continue
    elif line[0] == "if":
        expression = [line[i] for i in range(1, line.index("{"))]
        expression = expression_to_rpn(expression)
        eval(current_scope).append({
            "type": "if",
            "expression": expression,
            "code": []
        })
        current_scope += '[-1]["code"]'
    elif line[0] == "uint":
        eval(current_scope).append({
            "type": "set_variable",
            "name": line[1],
            "expression": line[3]
        })
    else:
        expression = expression_to_rpn(line)
        eval(current_scope).append({
            "type": "update_variable",
            "expression": expression
        })
print(syntax_tree)

data = []
bss = []
text = []

assignment_operator_lookup = {
    "=": "mov",
    "+=": "add",
    "-=": "sub",
    "*=": "mul",
    "/=": "div"
}

code_operator_lookup = {
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div"
}

for node in syntax_tree:
    if node["type"] == "set_variable":
        data.append(f"{node['name']} dd {node['expression']}")
    elif node["type"] == "update_variable":
        node["expression"] = expression_to_rpn("x = 4 - y * 3 + ( z + 2 ) * 4".split())
        # Short expression
        while True: # While node["expression"] keeps getting updated by for loop
            for index, token in enumerate(node["expression"]):
                if token in ["+", "-", "*", "/"]:
                    code_operator = node["expression"][index]
                    right = str(node["expression"][index - 1])
                    left = str(node["expression"][index - 2])
                    if str_is_float(left) and str_is_float(right):
                        del node["expression"][index - 2:index + 1]
                        node["expression"].insert(index - 2, eval(left + code_operator + right))
                        print(node["expression"])
                        break
            else:
                break
        # Expression to assembly
        unused_registers = ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]
        while True: # While there still are operators in expression
            for index, token in enumerate(node["expression"]):
                if token in code_operator_lookup:
                    break
            else: # If no more operators
                break
            code_operator = node["expression"].pop(index)
            right = str(node["expression"].pop(index - 1))
            left = str(node["expression"].pop(index - 2))

            if code_operator in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="]:
                text.append(f"mov {left}, {right}")
                break

            if left not in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                left_register = unused_registers.pop()
                text.append(f"mov {left_register}, {left}")
                left = left_register
                
            if (not str_is_float(right)) and (right not in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]):
                right_register = unused_registers.pop()
                text.append(f"mov {right_register}, {right}")
                right = right_register
            
            text.append(f"{code_operator_lookup[code_operator]} {left}, {right}")

            if right in ["r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rdi", "rsi", "rcx", "rbx", "rax"]:
                unused_registers.append(right)

            node["expression"].insert(index - 2, left)

print(data)
for line in text:
    print(line)

#     x = 4 - y * 3 + ( z + 2 ) * 4

#     x 4 y 3 * - z 2 + 4 * + =

# mov rax, y
# mul rax, 3

#     x 4 rax - z 2 + 4 * + =

# mov rbx, 4
# sub rbx, rax

#     x rbx z 2 + 4 * + =

# mov rax, z
# add rax, 2

#     x rbx rax 4 * + =

# mul rax, 4

#     x rbx rax + =

# add rbx, rax

#     x rbx =

# mov x, rax