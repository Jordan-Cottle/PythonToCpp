#! /usr/bin/env python

import os
import sys

from compiler.parser import translate_file

py_dir = "py"
cpp_dir = "cpp"
obj_dir = "obj"


def execute(system_call):
    print(system_call)
    os.system(system_call)


def find_files(root_dir, extension):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file_name in filenames:
            _, _extension = os.path.splitext(file_name)
            if _extension == extension:
                yield os.path.join(dirpath, file_name)


def replace_top_dir(path, target, new_ext=None):
    name, ext = os.path.splitext(path)
    if new_ext is not None:
        ext = new_ext
        if not ext.startswith("."):
            ext = f".{ext}"

    dirs = name.split("/")
    dirs[0] = target

    os.makedirs(os.path.join(*dirs[:-1]), exist_ok=True)
    return f"{os.path.join(*dirs)}{ext}"


def generate_cpp(path, output_path=None):
    if output_path is None:
        output_path = replace_top_dir(path, cpp_dir, ".cpp")

    with open(output_path, "w") as cpp_file:
        print(translate_file(path), file=cpp_file, end="")

    return output_path


def compile_cpp(path):
    output_path = replace_top_dir(path, obj_dir, ".o")
    execute(f"g++ -c -o {output_path} {path}")

    return output_path


def build(objects):
    execute(f"g++ -o main {' '.join(objects)}")


def main():
    project = sys.argv[1]
    for py_file in find_files(f"{py_dir}/{project}", ".py"):
        generate_cpp(py_file)

    for cpp_file in find_files(f"{cpp_dir}/{project}", ".cpp"):
        compile_cpp(cpp_file)

    build(tuple(find_files(f"{obj_dir}/{project}", ".o")))

    execute("./main")


if __name__ == "__main__":
    main()
