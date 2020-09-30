import os

from parser import translate_file

py_dir = "py"
cpp_dir = "cpp"


def generate_cpp(path):
    cpp_path = f"{cpp_dir}/{path.split('/')[-1].strip('.py')}.cpp"
    with open(cpp_path, "w") as cpp_file:
        print(translate_file(path), file=cpp_file, end="")

    return cpp_path


def compile_cpp(path):
    object_path = f"compiled{path.strip('.cpp')}.o"
    os.system(f"g++ -c -o {object_path} {path}")
    return object_path


def build(objects):
    main_target = objects[0]
    exe_name = main_target.split("/")[-1].strip(".o")
    os.system(f"g++ -o {exe_name} {' '.join(objects)}")


def build_project(directory):
    objects = []
    for target in os.listdir(directory):
        cpp_path = generate_cpp(f"{directory}/{target}")
        objects.append(compile_cpp(cpp_path))

    build(objects)


def main():
    for project_dir in os.listdir(py_dir):
        print(f"Building {project_dir}")
        build_project(f"{py_dir}/{project_dir}")

        print(f"Executing {project_dir}")
        os.system("./main")


if __name__ == "__main__":
    main()
