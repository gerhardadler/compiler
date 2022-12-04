from enum import Enum, auto
from dataclasses import dataclass
import utils

# Operators

class Associativity(Enum):
    LEFT_TO_RIGHT = auto()
    RIGHT_TO_LEFT = auto()


@dataclass
class Operator:
    name: str
    precedence: int
    asm: str
    associativity: Associativity


@dataclass
class LogicalOperator(Operator):
    associativity: Associativity = Associativity.LEFT_TO_RIGHT


@dataclass
class BitwiseOperator(Operator):
    associativity: Associativity = Associativity.LEFT_TO_RIGHT


@dataclass
class ComparisonOperator(Operator):
    associativity: Associativity = Associativity.LEFT_TO_RIGHT


@dataclass
class AssignmentOperator(Operator):
    associativity: Associativity = Associativity.LEFT_TO_RIGHT


@dataclass
class ArithmeticOperator(Operator):
    associativity: Associativity = Associativity.LEFT_TO_RIGHT


# BRACKETS

class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()


@dataclass
class Bracket():
    name: str
    direction: Direction


@dataclass
class RoundBracket(Bracket):
    pass


@dataclass
class CurlyBracket(Bracket):
    pass


@dataclass
class SquareBracket(Bracket):
    pass


# Var types

@dataclass
class VarType:
    name: str
    size: int

    def __post_init__(self):
        self.size_specifier = utils.size_to_specifier(self.size)


@dataclass
class UnsignedInt(VarType):
    pass


# Other

@dataclass
class Comma:
    name: str


@dataclass
class Semicolon:
    name: str


@dataclass
class AddressOf:
    name: str


@dataclass
class If:
    name: str


@dataclass
class Elif:
    name: str


@dataclass
class FuncDeclaration:
    name: str


@dataclass
class Return:
    name: str


@dataclass
class Syscall:
    name: str


@dataclass
class Number:
    name: int

    def __post_init__(self):
        self.size = self.get_number_size(self.name)

    def get_number_size(self, number: int) -> int:
        for i in [8, 16, 32, 64]:
            if number > 2 ** i:
                return i
        else:
            raise Exception("Number is too big")


@dataclass
class Var:
    name: str

    def add_info(self, var_type: VarType, rbp_diff: int, address_of: bool = False):
        self.var_type: VarType = var_type
        self.rbp_diff: int = rbp_diff
        self.address_of: bool = address_of