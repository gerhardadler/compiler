names = [
    # logical operators
    {"name": "&&", "type": "logical_operator", "precedence": 10,  "associativity": "left_to_right"},
    {"name": "||", "type": "logical_operator", "precedence": 11,  "associativity": "left_to_right"},

    # bitwise operators
    {"name": "<<", "type": "bitwise_operator", "precedence": 4,  "associativity": "left_to_right", "assembly": "shl"},
    {"name": ">>", "type": "bitwise_operator", "precedence": 4,  "associativity": "left_to_right", "assembly": "shr"},
    {"name": "&", "type": "bitwise_operator", "precedence": 7,  "associativity": "left_to_right", "assembly": "and"},
    {"name": "^", "type": "bitwise_operator", "precedence": 8,  "associativity": "left_to_right", "assembly": "xor"},
    {"name": "|", "type": "bitwise_operator", "precedence": 9,  "associativity": "left_to_right", "assembly": "or"},

    # comparison operators
    {"name": "==", "type": "comparison_operator", "precedence": 6, "associativity": "left_to_left", "assembly": "cmp"},
    {"name": "!=", "type": "comparison_operator", "precedence": 6, "associativity": "left_to_left", "assembly": "cmp"},
    {"name": "<", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},
    {"name": ">", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},
    {"name": "<=", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},
    {"name": ">=", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},

    # assignment operators
    {"name": "=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "mov"},
    {"name": "+=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "add"},
    {"name": "-=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "sub"},
    {"name": "*=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "mul"},
    {"name": "/=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "div"},

    # arithmetic operators
    {"name": "*", "type": "arithmetic_operator", "precedence": 2,  "associativity": "left_to_right", "assembly": "mul"},
    {"name": "/", "type": "arithmetic_operator", "precedence": 2,  "associativity": "left_to_right", "assembly": "div"},
    {"name": "+", "type": "arithmetic_operator", "precedence": 3,  "associativity": "left_to_right", "assembly": "add"},
    {"name": "-", "type": "arithmetic_operator", "precedence": 3,  "associativity": "left_to_right", "assembly": "sub"},

    # seperators
    {"name": ",", "type": "comma"},
    {"name": ";", "type": "semicolon"},

    # brackets
    {"name": "(", "type": "bracket"},
    {"name": ")", "type": "bracket"},
    {"name": "{", "type": "curly_bracket"},
    {"name": "}", "type": "curly_bracket"},
    {"name": "[", "type": "bracket"},
    {"name": "]", "type": "bracket"},

    # type declaration
    {"name": "uint8", "type": "type_declaration", "size": 8},
    {"name": "uint16", "type": "type_declaration", "size": 16},
    {"name": "uint32", "type": "type_declaration", "size": 32},
    {"name": "uint64", "type": "type_declaration", "size": 64},
    
    {"name": "if", "type": "if"},
    {"name": "elif", "type": "elif"},
    {"name": "def", "type": "function"},

    {"name": "syscall", "type": "syscall"}
]

def is_str_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def lexer(code):
    code = " ".join(code.split()) + " "

    output_tokens = []
    code_index = 0

    while code_index < len(code):
        first_seperator_index = -1 # if there is no more seperators, -1 will be used.
        for seperator in [dict["name"] for dict in names] + [" "]:
            seperator_index = code.find(seperator, code_index)
            if first_seperator_index == -1 or (seperator_index < first_seperator_index and seperator_index != -1):
                first_seperator_index = seperator_index
        
        current_word = code[code_index:first_seperator_index]

        if code[code_index] == " ":
            code_index += 1
            continue
        for name in names:
            if code.startswith(name["name"], code_index):
                output_tokens.append(name)
                code_index += len(name["name"]) - 1 # subtracting 1, as 1 is added later.
                break
        else: # nobreak
            if is_str_number(current_word):
                output_tokens.append({
                    "name": current_word,
                    "type": "number"
                })
                code_index += len(current_word) - 1 # subtracting 1, as 1 is added later.
            else:
                if code[first_seperator_index] == "(":
                    output_tokens.append({
                    "name": current_word,
                    "type": "function_name"
                })
                else:
                    output_tokens.append({
                        "name": current_word,
                        "type": "variable_name"
                    })
                code_index += len(current_word) - 1 # subtracting 1, as 1 is added later.

        code_index += 1
    
    return output_tokens