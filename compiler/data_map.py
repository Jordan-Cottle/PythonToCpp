from compiler import CompileError

from ast import (
    Add,
    Sub,
    Mult,
    Div,
    FloorDiv,
    Mod,
    Pow,
    LShift,
    RShift,
    BitOr,
    BitAnd,
    BitXor,
    UAdd,
    USub,
    Not,
    Invert,
    And,
    Or,
    Eq,
    NotEq,
    Lt,
    LtE,
    Gt,
    GtE,
)

OPERATORS = {
    Add: "+",
    Sub: "-",
    Mult: "*",
    Div: "/",
    FloorDiv: "/",
    Mod: "%",
    LShift: "<<",
    RShift: ">>",
    BitOr: "|",
    BitAnd: "&",
    BitXor: "^",
    UAdd: "+",
    USub: "-",
    Not: "!",
    Invert: "~",
    And: "&&",
    Or: "||",
    Eq: "==",
    NotEq: "!=",
    Lt: "<",
    LtE: "<=",
    Gt: ">",
    GtE: ">=",
}

TYPES = {
    "str": "std::string",
    "int": "int",
    "float": "double",
    "List": "std::vector",
    "None": "void",
}

INCLUDES = {
    "std::string": "<string>",
    "std::vector": "<vector>",
}


class UnknownTypeError(CompileError):
    """ Raised when a conversion from python type hint to cpp is unknown. """


def get_type(name):
    """Get the c++ type for name.

    Also returns the required include, if any.
    """

    cpp_type = TYPES.get(name)

    if cpp_type is None:
        raise UnknownTypeError(f"No conversion for {name} is known")

    return cpp_type, INCLUDES.get(cpp_type)
