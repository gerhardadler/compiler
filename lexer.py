symbols = [
    # comparison operators
    {"symbol": "==", "type": "comparison_operator", "precedence": 6, "associativity": "left_to_left", "assembly": "cmp"},
    {"symbol": "!=", "type": "comparison_operator", "precedence": 6, "associativity": "left_to_left", "assembly": "cmp"},
    {"symbol": "<", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},
    {"symbol": ">", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},
    {"symbol": "<=", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},
    {"symbol": ">=", "type": "comparison_operator", "precedence": 5, "associativity": "left_to_left", "assembly": "cmp"},

    # assignment operators
    {"symbol": "=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "mov"},
    {"symbol": "+=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "add"},
    {"symbol": "-=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "sub"},
    {"symbol": "*=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "mul"},
    {"symbol": "/=", "type": "assignment_operator", "precedence": 12, "associativity": "right_to_left", "assembly": "div"},

    # arithmetic operators
    {"symbol": "*", "type": "arithmetic_operator", "precedence": 2,  "associativity": "left_to_right", "assembly": "mul"},
    {"symbol": "/", "type": "arithmetic_operator", "precedence": 2,  "associativity": "left_to_right", "assembly": "div"},
    {"symbol": "+", "type": "arithmetic_operator", "precedence": 3,  "associativity": "left_to_right", "assembly": "add"},
    {"symbol": "-", "type": "arithmetic_operator", "precedence": 3,  "associativity": "left_to_right", "assembly": "sub"},

    # seperators
    {"symbol": ",", "type": "seperator"},
    {"symbol": ";", "type": "seperator"},

    # brackets
    {"symbol": "(", "type": "bracket"},
    {"symbol": ")", "type": "bracket"},
    {"symbol": "{", "type": "curly_bracket"},
    {"symbol": "}", "type": "curly_bracket"},
    {"symbol": "[", "type": "bracket"},
    {"symbol": "]", "type": "bracket"},
]

keywords = [
    # type declaration
    {"symbol": "uint", "type": "type_declaration"},
    
    {"symbol": "if", "type": "keyword"}
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
        for seperator in [dict["symbol"] for dict in symbols] + [" "]:
            seperator_index = code.find(seperator, code_index)
            if first_seperator_index == -1 or (seperator_index < first_seperator_index and seperator_index != -1):
                first_seperator_index = seperator_index
        
        current_word = code[code_index:first_seperator_index]

        if code[code_index] == " ":
            code_index += 1
            continue
        for symbol in symbols:
            if code.startswith(symbol["symbol"], code_index):
                output_tokens.append(symbol)
                code_index += len(symbol["symbol"]) - 1 # subtracting 1, as 1 is added later.
                break
        else:
            for keyword in keywords:
                if current_word == keyword["symbol"]:
                    output_tokens.append(keyword)
                    code_index += len(current_word) - 1 # subtracting 1, as 1 is added later.
                    break
            else:
                if is_str_number(current_word):
                    output_tokens.append({
                        "symbol": current_word,
                        "type": "number"
                    })
                    code_index += len(current_word) - 1 # subtracting 1, as 1 is added later.
                else:
                    output_tokens.append({
                        "symbol": current_word,
                        "type": "variable_name"
                    })
                    code_index += len(current_word) - 1 # subtracting 1, as 1 is added later.

        code_index += 1
    
    # code = re.sub("\s+", " ", code)
    return output_tokens