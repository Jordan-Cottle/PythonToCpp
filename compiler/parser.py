#! /usr/bin/env python3

import os
import sys
import ast
from ast import Name, Call

from compiler import get_type, CompileError, OPERATORS

from collections import defaultdict


def translate_file(path):
    converter = Converter(path)
    converter.compile()

    return converter.report()


def get_return_annotation(function_source):
    header = function_source.split("\n")[0]
    if ") -> " not in header:
        raise CompileError("Functions must have a return type specified!")

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
            self.visit(arg)

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

    def visit_Assign(self, node):
        """ Handle assignment statements. """

        target = node.targets[0]
        value = node.value
        print(f"Handling assign: {target.id} = {value}")

        if target.id not in self.delcared:
            self += "auto "
            self.delcared.add(target.id)

        # Parse Name before assignment operator
        self.visit_Name(target)
        self += " = "
        self.visit(value)

        self.end_line()

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

    def visit_FunctionDef(self, node):
        """ Handle parsing functions. """

        name = node.name
        args = node.args
        body = node.body
        print(f"Handling function definition: {name} {args}")

        function_definition = ast.get_source_segment(open(self.path).read(), node)

        return_type = self.get_type(get_return_annotation(function_definition))

        self += f"{return_type} {name} ("

        self.visit(args)

        self.end_line(") {")

        with CompileFlag(self, "indent"):
            for sub_node in body:
                self.visit(sub_node)

        self.end_line("}")

    def visit_arguments(self, node):
        args = node.args
        print(f"Handling function args: {args}")
        if not args:
            return

        for i, arg in enumerate(args):
            self.visit(arg)
            if i + 1 < len(args):
                self += ", "

    def visit_arg(self, node):
        """ Handle definitions of function arguments. """
        arg = node.arg
        print(f"Handling function arg: {arg}")

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
        op = OPERATORS.get(type(node.op))

        if not op:
            raise CompileError(f"{node.op} is an unsupported binary operator")

        self.visit(node.left)
        self += f" {op} "
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        print(f"Handling unary operator: {node.op}")
        op = OPERATORS.get(type(node.op))

        if not op:
            raise CompileError(f"{node.op} is an unsupported unary operator")

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

    def __iadd__(self, value):
        indent = "\t" * (self.indent * self.line_start)

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