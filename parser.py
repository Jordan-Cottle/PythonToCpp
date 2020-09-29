#! /usr/bin/env python3

import sys
import ast
from _ast import Name, Call
from pprint import pprint


def main():
    file = sys.argv[1]
    with open(file, "r") as source:
        tree = ast.parse(source.read())

    converter = Converter()
    converter.visit(tree)

    cpp_name = file.strip(".py") + ".cpp"
    with open(cpp_name, "w") as cpp_file:
        print(converter.report(), file=cpp_file)


class Converter(ast.NodeVisitor):
    def __init__(self):
        self.code = []
        self.includes = set()

        self.delcared = set()

        self.indent = 0
        self.line_start = True

    def end_line(self, text=";"):
        self += f"{text}\n"
        self.line_start = True

    def convert_print(self, node):
        """ Handle print function. """

        self.includes.add("<iostream>")

        self += "std::cout"
        for arg in node.args:
            self += " << "
            self.visit(arg)

        self += r' << "\n"'

    def visit_Constant(self, node):
        """ Handle constants specified in the source. """

        value = node.value
        print(f"Handling constant: {value}")

        if isinstance(value, str):
            self += f'"{value}"'
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
            print("WARNING: C++ does not support named arguments")

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

        if name == "main":
            return_type = "int"
        else:
            return_type = "auto"
        self += f"{return_type} {name} ("

        if args:
            self.visit(args)
        self.end_line(") {")

        self.indent += 1
        for sub_node in body:
            self.visit(sub_node)

        self.indent -= 1
        self.end_line("}")

    def visit_arguments(self, node):
        """ Handle definitions of function arguments. """

    def report(self):
        string = []
        for include in self.includes:
            string.append(f"#include {include}")

        string.append("\n\n")
        for item in self.code:
            string.append(item)

        return "".join(string)

    def __iadd__(self, value):
        indent = "\t" * (self.indent * self.line_start)

        self.line_start = False
        self.code.append(f"{indent}{value}")

        return self


if __name__ == "__main__":
    main()
