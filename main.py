import json
import jsons

from lexer import lexer
from parser import parser

code = """
uint x = 2;

if x == 2 {
    x = 3;
}
"""

lexed_code = lexer(code)
print(lexed_code)
print("\n"*2)
syntax_tree = parser(lexed_code)
print(syntax_tree)

print(json.dumps(jsons.dump(syntax_tree, strip_privates=True), indent=2))