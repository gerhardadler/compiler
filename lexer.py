from dataclasses import dataclass
from enum import Enum, auto


class Associativity(Enum):
    LEFT_TO_RIGHT = auto()
    RIGHT_TO_LEFT = auto()


class Type(Enum):
    LOGICAL_OPERATOR = auto()
    BITWISE_OPERATOR = auto()
    COMPARISON_OPERATOR = auto()
    ARITHMETIC_OPERATOR = auto()
    ASSIGNMENT_OPERATOR = auto()


@dataclass
class Symbol:
    name: str
    type: Type


@dataclass
class Operator:
    type: Type
    name: str
    precedence: int
    associativity: Associativity
    asm: str


symbols = [
    # logical operators
    Operator(Type.LOGICAL_OPERATOR, "&&", 10, Associativity.LEFT_TO_RIGHT, "no"),
    Operator(Type.LOGICAL_OPERATOR, "||", 11, Associativity.LEFT_TO_RIGHT, "no"),

    # bitwise operators
    Operator(Type.BITWISE_OPERATOR, "<<", 4, Associativity.LEFT_TO_RIGHT, "shl"),
    Operator(Type.BITWISE_OPERATOR, ">>", 4, Associativity.LEFT_TO_RIGHT, "shr"),
    Operator(Type.BITWISE_OPERATOR, "&", 7, Associativity.LEFT_TO_RIGHT, "and"),
    Operator(Type.BITWISE_OPERATOR, "^", 8, Associativity.LEFT_TO_RIGHT, "xor"),
    Operator(Type.BITWISE_OPERATOR, "|", 9, Associativity.LEFT_TO_RIGHT, "or"),

    # comparison operators
    Operator(Type.COMPARISON_OPERATOR, "==", 6, Associativity.LEFT_TO_RIGHT, "cmp"),
    Operator(Type.COMPARISON_OPERATOR, "!=", 6, Associativity.LEFT_TO_RIGHT, "cmp"),
    Operator(Type.COMPARISON_OPERATOR, "<", 6, Associativity.LEFT_TO_RIGHT, "cmp"),
    Operator(Type.COMPARISON_OPERATOR, ">", 6, Associativity.LEFT_TO_RIGHT, "cmp"),
    Operator(Type.COMPARISON_OPERATOR, "<=", 6, Associativity.LEFT_TO_RIGHT, "cmp"),
    Operator(Type.COMPARISON_OPERATOR, ">=", 6, Associativity.LEFT_TO_RIGHT, "cmp"),
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

    {"name": "def", "type": "function_declaration"},
    {"name": "ret", "type": "return"},

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
        if code[code_index] == " ":
            code_index += 1
            continue

        for symbol in symbols:
            if code.startswith(symbol["name"], code_index):
                output_tokens.append(symbol)
                code_index += len(symbol["name"]) - 1 # subtracting 1, as 1 is added later.
                break
        else: # nobreak
            first_seperator_index = -1 # if there is no more seperators, -1 will be used.
            for seperator in [dict["name"] for dict in symbols] + [" "]:
                seperator_index = code.find(seperator, code_index)
                if first_seperator_index == -1 or (seperator_index < first_seperator_index and seperator_index != -1):
                    first_seperator_index = seperator_index
            
            current_word = code[code_index:first_seperator_index]

            for keyword in keywords:
                if current_word == keyword["name"]:
                    output_tokens.append(keyword)
                    code_index += len(keyword["name"]) - 1 # subtracting 1, as 1 is added later.
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