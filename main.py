from os import system

import json
import jsons

from lexer import lexer
from parser import parser
from compiler import compiler

code = """
def main() {
    uint32 x = 65;
    print(x);
}

def print(uint32 a) {
    syscall(1, 1, a, 8);
}
"""

lexed_code = lexer(code)
print(*lexed_code, sep="\n")
syntax_tree = parser(lexed_code)
# print(syntax_tree)

# ugly way to print syntax tree, but just for testing
print(json.dumps(jsons.dump(syntax_tree, strip_privates=True), indent=2))

assembly = compiler(syntax_tree)

print("# DATA SECTION")
for instruction in assembly["data"]:
    print(instruction)

print("\n# BSS SECTION")
for instruction in assembly["bss"]:
    print(instruction)

print("\n# TEXT SECTION")
for instruction in assembly["text"]:
    print(instruction)

if input("write to \"test.asm\"? (Y/n)") != "n":
    with open("test.asm", "w") as f:
        f.write("\n".join(assembly["text"]))

if input("Assemble? (Y/n)") != "n":
    system("./assemble.sh test")
    system("./test")