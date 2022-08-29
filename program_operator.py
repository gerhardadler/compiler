class ProgramOperator:
    def __init__(self, symbol, precedence, associativity, assembly, is_assignment):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity
        self.assembly = assembly
        self.is_assignment = is_assignment
    
    def 

        operators = [
            {"symbol": "*", "precedence": 2,  "associativity": "left_to_right", "assembly": "mul", "assignment": False},
            {"symbol": "/", "precedence": 2,  "associativity": "left_to_right", "assembly": "div", "assignment": False},
            {"symbol": "+", "precedence": 3,  "associativity": "left_to_right", "assembly": "add", "assignment": False},
            {"symbol": "-", "precedence": 3,  "associativity": "left_to_right", "assembly": "sub", "assignment": False},
            {"symbol": "=", "precedence": 12, "associativity": "right_to_left", "assembly": "mov", "assignment": True}
        ]