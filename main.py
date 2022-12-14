from os import system

import json
import jsons

from lexer import lexer
from parser import parser
from compiler import compiler

code = """
def print(u64 value) {
    syscall(1, 1, @value, 8);
}

def main() {
    u32 x = 1;
    u32 y = 2;
    if x == 1 {
        y = 3;
    }
}
"""

lexed_code = lexer(code)
print(*lexed_code, sep="\n")
syntax_tree = parser(lexed_code)
# print(syntax_tree)

# ugly way to print syntax tree, but just for testing
print(json.dumps(jsons.dump(syntax_tree, strip_privates=True), indent=2))

asm = compiler(syntax_tree)

print("# DATA SECTION")
for instruction in asm["data"]:
    print(instruction)

print("\n# BSS SECTION")
for instruction in asm["bss"]:
    print(instruction)

print("\n# TEXT SECTION")
for instruction in asm["text"]:
    print(instruction)

if input("write to \"test.asm\"? (Y/n)") != "n":
    with open("test.asm", "w") as f:
        f.write("\n".join(asm["text"]))

if input("Assemble? (Y/n)") != "n":
    system("./assemble.sh test")
    system("./test")