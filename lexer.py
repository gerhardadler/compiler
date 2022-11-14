import re

symbols = [
    # logical operators
    {"name": "&&", "type": "logical_operator", "precedence": 10, "associativity": "left_to_right"},
    {"name": "||", "type": "logical_operator", "precedence": 11, "associativity": "left_to_right"},

    # bitwise operators
    {"name": "<<", "type": "bitwise_operator", "precedence": 4, "associativity": "left_to_right", "asm": "shl"},
    {"name": ">>", "type": "bitwise_operator", "precedence": 4, "associativity": "left_to_right", "asm": "shr"},
    {"name": "&", "type": "bitwise_operator", "precedence": 7, "associativity": "left_to_right", "asm": "and"},
    {"name": "^", "type": "bitwise_operator", "precedence": 8, "associativity": "left_to_right", "asm": "xor"},
    {"name": "|", "type": "bitwise_operator", "precedence": 9, "associativity": "left_to_right", "asm": "or"},

    # comparison operators
    {"name": "==", "type": "comparison_operator", "precedence": 6, "associativity": "left_to_left", "asm": "cmp"},
    {"name": "!=", "type": "comparison_operator", "precedence": 6, "associativity": "left_to_left", "asm": "cmp"},
    {"name": "<", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "asm": "cmp"},
    {"name": ">", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "asm": "cmp"},
    {"name": "<=", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "asm": "cmp"},
    {"name": ">=", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "asm": "cmp"},

    # assignment operators
    {"name": "=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "mov"},
    {"name": "+=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "add"},
    {"name": "-=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "sub"},
    {"name": "*=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "mul"},
    {"name": "/=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "asm": "div"},

    # arithmetic operators
    {"name": "*", "type": "arithmetic_operator", "precedence": 2, "associativity": "left_to_right", "asm": "mul"},
    {"name": "/", "type": "arithmetic_operator", "precedence": 2, "associativity": "left_to_right", "asm": "div"},
    {"name": "+", "type": "arithmetic_operator", "precedence": 3, "associativity": "left_to_right", "asm": "add"},
    {"name": "-", "type": "arithmetic_operator", "precedence": 3, "associativity": "left_to_right", "asm": "sub"},

    # seperators
    {"name": ",", "type": "comma"},
    {"name": ";", "type": "semicolon"},

    # brackets
    {"name": "(", "type": "round_bracket"},
    {"name": ")", "type": "round_bracket"},
    {"name": "{", "type": "curly_bracket"},
    {"name": "}", "type": "curly_bracket"},
    {"name": "[", "type": "bracket"},
    {"name": "]", "type": "bracket"},

    {"name": "@", "type": "address_of"}
]
symbols.sort(reverse=True, key=lambda symbol: len(symbol["name"])) # avoids overlapping as symbols with longer names come first

keywords = [
    # type declaration
    {"name": "u8", "type": "type_declaration", "size": 8},
    {"name": "u16", "type": "type_declaration", "size": 16},
    {"name": "u32", "type": "type_declaration", "size": 32},
    {"name": "u64", "type": "type_declaration", "size": 64},
    
    {"name": "if", "type": "if"},
    {"name": "elif", "type": "elif"},
    {"name": "def", "type": "function"},

    {"name": "syscall", "type": "syscall"}
]

def str_is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def lexer(code): # TODO symbols more than one character big doesnt work
    code = re.findall(r"[A-Za-z0-9_]+|\S", code)

    output_tokens = []

    token_index = 0
    while token_index < len(code):
        for symbol in symbols + keywords:
            if code[token_index] == symbol["name"]:
                output_tokens.append(symbol)
                break
        else: # if token isn't a symbol
            if str_is_number(code[token_index]):
                output_tokens.append({
                    "name": code[token_index],
                    "type": "number"
                })
            elif code[token_index + 1] == "(":
                output_tokens.append({
                    "name": code[token_index],
                    "type": "function_name"
                })
            else:
                output_tokens.append({
                    "name": code[token_index],
                    "type": "variable_name"
                })
        token_index += 1
    
    return output_tokens