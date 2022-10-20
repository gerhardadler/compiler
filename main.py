import json
import jsons

from lexer import lexer
from parser import parser
from compiler import compiler

code = """
def main() {
    uint x = 3;
    uint y = 2;

    x = y + 4 - x + 2;

    bean(var, b, 3);

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