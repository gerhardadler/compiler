import symbols

symbols_list = [
    # logical operators
    symbols.LogicalOperator("&&", 10, "no"),
    symbols.LogicalOperator("||", 11, "no"),

    # bitwise operators
    symbols.BitwiseOperator("<<", 4, "shl"),
    symbols.BitwiseOperator(">>", 4, "shr"),
    symbols.BitwiseOperator("&", 7, "and"),
    symbols.BitwiseOperator("^", 8, "xor"),
    symbols.BitwiseOperator("|", 9, "or"),

    # comparison operators
    symbols.ComparisonOperator("==", 6, "cmp"),
    symbols.ComparisonOperator("!=", 6, "cmp"),
    symbols.ComparisonOperator("<", 5, "cmp"),
    symbols.ComparisonOperator(">", 5, "cmp"),
    symbols.ComparisonOperator("<=", 5, "cmp"),
    symbols.ComparisonOperator(">=", 5, "cmp"),

    # assignment operators
    symbols.AssignmentOperator("=", 12, "mov"),
    symbols.AssignmentOperator("+=", 12, "add"),
    symbols.AssignmentOperator("-=", 12, "sub"),
    symbols.AssignmentOperator("*=", 12, "mul"),
    symbols.AssignmentOperator("/=", 12, "div"),

    # arithmetic operators
    symbols.ArithmeticOperator("*", 2, "mul"),
    symbols.ArithmeticOperator("/", 2, "div"),
    symbols.ArithmeticOperator("+", 3, "add"),
    symbols.ArithmeticOperator("-", 3, "sub"),

    # seperators
    symbols.Comma(","),
    symbols.Semicolon(";"),

    # brackets
    symbols.RoundBracket("(", symbols.Direction.LEFT),
    symbols.RoundBracket(")", symbols.Direction.LEFT),
    symbols.CurlyBracket("{", symbols.Direction.LEFT),
    symbols.CurlyBracket("}", symbols.Direction.LEFT),
    symbols.SquareBracket("[", symbols.Direction.LEFT),
    symbols.SquareBracket("]", symbols.Direction.LEFT),

    symbols.AddressOf("@")
]
symbols_list.sort(reverse=True, key=lambda symbol: len(symbol.name)) # avoids overlapping as symbols with longer names come first

keywords = [
    # type declaration
    symbols.UnsignedInt("u8", 8),
    symbols.UnsignedInt("u16", 16),
    symbols.UnsignedInt("u32", 32),
    symbols.UnsignedInt("u64", 64),
    
    symbols.If("if"),
    symbols.Elif("elif"),

    symbols.FuncDeclaration("def"),
    symbols.Return("ret"),

    symbols.Syscall("syscall")
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

        for symbol in symbols_list:
            if code.startswith(symbol.name, code_index):
                output_tokens.append(symbol)
                code_index += len(symbol.name) - 1 # subtracting 1, as 1 is added later.
                break
        else: # nobreak
            first_seperator_index = -1 # if there is no more seperators, -1 will be used.
            for seperator in [dict.name for dict in symbols_list] + [" "]:
                seperator_index = code.find(seperator, code_index)
                if first_seperator_index == -1 or (seperator_index < first_seperator_index and seperator_index != -1):
                    first_seperator_index = seperator_index
            
            current_word = code[code_index:first_seperator_index]

            for keyword in keywords:
                if current_word == keyword.name:
                    output_tokens.append(keyword)
                    code_index += len(keyword.name) - 1 # subtracting 1, as 1 is added later.
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
                        "type": "func_name"
                    })
                    else:
                        output_tokens.append({
                            "name": current_word,
                            "type": "var_name"
                        })
                    code_index += len(current_word) - 1 # subtracting 1, as 1 is added later.

        code_index += 1
    
    return output_tokens