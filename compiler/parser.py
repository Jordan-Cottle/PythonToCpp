#! /usr/bin/env python3

import ast
import os
import sys
from ast import Attribute, Call, Constant, Expr, FunctionDef, If, Name
from collections import defaultdict

from compiler import (
    CompileError,
    UnknownTypeError,
    get_exception_type,
    get_operator,
    get_type,
    TYPES,
)

SPACES_PER_TAB = 4


class FunctionTypeError(CompileError):
    """ Functions must have their return types annotated. """


def translate_file(path):
    converter = Converter(path)
    converter.compile()

    return converter.report()


def get_return_annotation(function_source):
    header = function_source.split("\n")[0]
    if ") -> " not in header:
        raise FunctionTypeError("Functions must have a return type specified!")

    type_ = header.split(") -> ")[-1].strip(":")

    return type_


class CompileFlag:
    def __init__(self, parser, name):
        self.parser = parser
        self.name = name

    @property
    def value(self):
        try:
            return getattr(self.parser, self.name)
        except AttributeError:
            return 0

    @value.setter
    def value(self, new_value):
        setattr(self.parser, self.name, new_value)

    def __enter__(self):
        self.value += 1
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.value -= 1


class Converter(ast.NodeVisitor):
    def __init__(self, file_path):
        self.path = os.path.abspath(file_path)
        self.line_no = 0

        self.current_class = ""
        self.code = []
        self.includes = set()

        self.delcared = set()

        self.flags = defaultdict(bool)

        with open(self.path, "r") as source:
            self.source = source.read()
            self.tree = ast.parse(
                self.source,
                filename=self.path,
            )

        def set_attribute(self, name, value):
            if name in self.__dict__:
                super().__setattr__(name, value)
            else:
                self.flags[name] = value

        self.__setattr__ = set_attribute

    def compile(self):
        self.visit(self.tree)

    def __getattr__(self, name):
        if name in dir(self):
            return super().__getattribute__(name)

        if name.startswith("visit"):
            return lambda node: self.generic_visit(node)

        return self.flags[name]

    def get_type(self, type_):
        cpp_type, include = get_type(type_)

        if include:
            self.includes.add(include)

        return cpp_type

    def file_link(self, line_no):
        return f'<File "{self.path}", line {line_no}>'

    def end_line(self, text=";"):
        self += f"{text}\n"
        self.line_start = True

    def convert_print(self, node):
        """ Handle print function. """

        self.includes.add("<iostream>")

        self += "std::cout"
        for arg in node.args:
            self += " << "
            print(f"Print conversion visiting: {arg}")

            if isinstance(arg, Name) or isinstance(arg, Constant):
                self.visit(arg)
            else:
                self += "("
                self.visit(arg)
                self += ")"

        self += r' << "\n"'

    def visit(self, node):
        if hasattr(node, "lineno"):
            self.line_no = node.lineno

        try:
            super().visit(node)
        except CompileError as error:
            file_link = self.file_link(self.line_no)

            if file_link not in str(error):
                raise type(error)(
                    f"{file_link} failed to compile due to: {error}"
                ) from error

            raise

    def visit_Constant(self, node):
        """ Handle constants specified in the source. """

        value = node.value
        print(f"Handling constant: {value}")

        if isinstance(value, str):
            self += f'"{value}"'
        elif isinstance(value, bool):
            self += str(value).lower()
        else:
            self += value

    def visit_List(self, node):
        """ Handle List literals. """

        elements = node.elts

        self.end_line("{")
        with CompileFlag(self, "indent"):
            for i, element in enumerate(elements):
                self.visit(element)
                if i + 1 < len(elements):
                    self.end_line(",")
                else:
                    self.end_line("")

        self += "}"

    def visit_Tuple(self, node):
        self.visit_List(node)

    def visit_Name(self, node):
        """ Handle variable names in the source. """

        name = node.id
        print(f"Handling variable: {name}")

        self += name

    def visit_Expr(self, node):
        """ Handle expressions. """

        print(f"Handling Expr: {node}")
        self.generic_visit(node)
        self.end_line()

    def assign(self, value):

        self += " = "
        self.visit(value)

        self.end_line()

    def visit_Assign(self, node):
        """ Handle assignment statements. """

        target = node.targets[0]
        value = node.value
        print(f"Handling assign: {target} = {value}")

        print(type(target))
        # Parse Attribute/Name before assignment operator
        if isinstance(target, Attribute):
            self.visit(target)
        else:
            if target.id not in self.delcared:
                self += "auto "
                self.delcared.add(target.id)
            self.visit_Name(target)

        self.assign(value)

    def visit_AnnAssign(self, node):
        target = node.target
        annotation = node.annotation
        value = node.value

        cpp_type = self.get_type(annotation.id)

        self += f"{cpp_type} "

        self.visit(target)

        if value:
            self.assign(value)
        else:
            self.end_line()

    def visit_AugAssign(self, node):

        target = node.target
        op = node.op
        value = node.value

        self.visit(target)

        operator = get_operator(op)

        print(f"Handling augmented assign: {operator}")

        self += f" {operator}= "

        self.visit(value)
        self.end_line()

    def visit_Attribute(self, node):
        value = node.value
        attr = node.attr

        if isinstance(value, Name):
            name = value.id

        print(f"Processing attribute: {name}.{attr}")

        if name == "self":
            self += "this->"
        else:
            self += f"{name}."

        self += f"{attr}"

    def visit_Call(self, node):
        """ Handle function calls. """

        func = node.func
        args = node.args
        keywords = node.keywords

        if keywords:
            raise CompileError("C++ does not support named arguments")

        if isinstance(func, Name):
            if func.id == "print":
                self.convert_print(node)
                return

            if func.id in TYPES:
                func.id = self.get_type(func.id)

        print(f"Handling function call: {func}")

        self.visit(func)
        self += "("
        if args:
            for arg in args[:-1]:
                self.visit(arg)
                self += ", "
            self.visit(args[-1])

        self += ")"

    def visit_Return(self, node):
        """ Handle return statements. """

        print(f"Handling return: {type(node.value)}")
        self += "return "
        self.visit(node.value)
        self.end_line()

    def handle_body(self, body):
        with CompileFlag(self, "indent"):
            for node in body:
                if isinstance(node, FunctionDef):
                    if node.name == "__init__":
                        node.name = name

                self.visit(node)

    def visit_FunctionDef(self, node):
        """ Handle parsing functions. """

        name = node.name
        args = node.args
        body = node.body
        print(f"Handling function definition: {name} {args}")

        function_definition = ast.get_source_segment(open(self.path).read(), node)

        try:
            return_type = self.get_type(get_return_annotation(function_definition))
        except FunctionTypeError:
            if node.name == self.current_class:
                return_type = ""
            else:
                raise

        self += f"{return_type} {name} ("

        self.visit(args)

        self.end_line(") {")
        self.handle_body(body)
        self.end_line("}")

    def visit_arguments(self, node):
        args = node.args
        print(f"Handling function args: {args}")
        if not args:
            return

        for i, arg in enumerate(args):
            skipped = self.visit_arg(arg)
            if i + 1 < len(args) and not skipped:
                self += ", "

    def visit_arg(self, node):
        """ Handle definitions of function arguments. """
        arg = node.arg
        print(f"Handling function arg: {arg}")

        if arg == "self" and self.current_class:
            return True

        annotation = node.annotation
        if annotation is None:
            raise CompileError(f"Unknown type for {arg}")

        if isinstance(annotation, Name):
            type_ = annotation.id
        else:
            type_ = annotation.value

        cpp_type = self.get_type(type_)

        print(f"Handling {type_} {arg}: {cpp_type}")
        self += f"{cpp_type} {arg}"

    def visit_BinOp(self, node):
        print(f"Handling binary operator: {node.op}")
        op = get_operator(node.op)

        self.visit(node.left)
        self += f" {op} "
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        print(f"Handling unary operator: {node.op}")
        op = get_operator(node.op)

        self += op
        self.visit(node.operand)

    def visit_BoolOp(self, node):
        print(f"Handling boolean operator: {node.op}")
        op = OPERATORS.get(type(node.op))

        if not op:
            raise CompileError(f"{node.op} is an unsupported binary operator")

        for i, value in enumerate(node.values):
            self.visit(value)
            if i + 1 < len(node.values):
                self += f" {op} "

    def visit_Compare(self, node):
        left = node.left

        ops = node.ops

        operands = node.comparators

        last_operand = left
        for op, operand in zip(ops, operands):
            op = get_operator(op)

            if last_operand != left:
                self += " && "

            self.visit(last_operand)
            self += f" {op} "
            self.visit(operand)

            last_operand = operand

    def handle_test(self, test):
        self += "("
        self.visit(test)
        self.end_line(")")

    def visit_If(self, node):
        test = node.test

        body = node.body
        orelse = node.orelse

        self += "if "
        self.handle_test(test)
        self.end_line("{")

        self.handle_body(body)

        if len(orelse) > 1:
            raise CompileError("More than one elif node, unknown action")

        if orelse:
            else_node = orelse[0]
            if isinstance(else_node, If):
                self += "}else "
                self.visit_If(else_node)
            else:
                self.end_line("}else {")

                with CompileFlag(self, "indent"):
                    self.visit(else_node)

                self.end_line("}")
        else:
            self.end_line("}")

    def visit_For(self, node):

        target = node.target

        if not isinstance(target, Name):
            raise CompileError("C++ does not support multiple targets in a loop")

        if node.orelse:
            raise CompileError("C++ does not support else statements on loops")

        iterable = node.iter

        self += "for (auto& "
        self.visit(target)
        self += " : "
        self.visit(iterable)

        self.end_line(") {")
        self.handle_body(node.body)
        self.end_line("}")

    def visit_While(self, node):

        if node.orelse:
            raise CompileError("C++ does not support else statements on for loops")

        self += "while "
        self.handle_test(node.test)
        self.end_line("{")

        self.handle_body(node.body)
        self.end_line("}")

    def visit_Break(self, node):
        self.end_line("break;")

    def visit_Continue(self, node):
        self.end_line("continue;")

    def visit_ClassDef(self, node):
        name = node.name
        bases = node.bases
        body = node.body

        self.current_class = name

        extends = ", ".join(base.id for base in bases)
        if extends:
            extends = f": {extends}"

        self.end_line(f"struct {name}{extends} {{")

        self.handle_body(body)

        self.end_line("};")
        self.current_class = ""

    def visit_Try(self, node):

        if node.orelse:
            raise CompileError("C++ does not support else statements on try blocks")

        if node.finalbody:
            raise CompileError("C++ does not support finally statements on try blocks")

        self.end_line("try {")

        self.handle_body(node.body)
        self.end_line("}")

        for handler in node.handlers:
            self.visit_Handler(handler)

    def visit_Handler(self, node):

        type_ = node.type
        name = node.name
        print(f"Hanlind exception handler {type_.id} {name}")

        try:
            cpp_type = get_exception_type(type_.id)
        except UnknownTypeError:
            cpp_type = self.get_type(type_.id)

        self.end_line(f"catch ({cpp_type}& {name}){{")
        self.handle_body(node.body)
        self.end_line("}")

    def visit_Raise(self, node):

        self += "throw"
        exc = node.exc

        if exc is not None:
            self += " "
            self.visit(exc)

        self.end_line()

    def __iadd__(self, value):
        indent = " " * (SPACES_PER_TAB * self.indent * self.line_start)

        self.line_start = False

        string = f"{indent}{value}"
        print(f"Adding: {string}")
        self.code.append(string)

        return self

    def report(self):
        string = []
        for include in self.includes:
            string.append(f"#include {include}\n")

        string.append("\n\n")
        for item in self.code:
            string.append(item)

        return "".join(string)
