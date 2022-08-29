from expression import Expression

code = """
uint x = 3

x = 2

if x == 3 {
    x = 4
}
"""

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
        expression = Expression([line[i] for i in range(1, line.index("{"))])
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
        eval(current_scope).append({
            "type": "update_variable",
            "expression": Expression(line)
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
        node["expression"] = Expression("x = 4 - y * 3 + ( z + 2 ) * 4".split())
        data, bss, text = node["expression"].to_assembly()

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