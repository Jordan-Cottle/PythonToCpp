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

EXCEPTIONS = {
    "Exception": "std::exception",
    "IndexError": "std:out_of_range",
    "ValueError": "std:invalid_argument",
    "RuntimeError": "std::runtime_error",
}

TYPES = {
    "str": "std::string",
    "int": "int",
    "float": "double",
    "List": "std::vector",
    "list": "std::vector",
    "None": "void",
    "bool": "bool",
    **EXCEPTIONS,
}


INCLUDES = {
    "std::string": "<string>",
    "std::vector": "<vector>",
}


class UnknownTypeError(CompileError):
    """ Raised when a conversion from python type hint to cpp is unknown. """


class UnknownOperatorError(CompileError):
    """ Raised when a conversion from python operator to cpp is unknown. """


def get_type(name):
    """Get the c++ type for name.

    Also returns the required include, if any.
    """

    cpp_type = TYPES.get(name)

    if cpp_type is None:
        raise UnknownTypeError(f"No conversion for {name} is known")

    return cpp_type, INCLUDES.get(cpp_type)


def get_operator(op_node):

    try:
        return OPERATORS[type(op_node)]
    except KeyError:
        raise UnknownOperatorError(
            f"{op_node.op} is an unsupported binary operator"
        ) from None


def get_exception_type(name):

    try:
        return EXCEPTIONS[name]
    except KeyError:
        raise UnknownTypeError(f"{name} not recognized as a c++ exception")