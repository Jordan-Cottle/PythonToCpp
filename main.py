import sys
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

def main():
    targets = sys.argv[1:]
    objects = []
    for target in targets:
        cpp_path = generate_cpp(target)
        objects.append(compile_cpp(cpp_path))

    build(objects)

    os.system("./main")
    

if __name__ == "__main__":
    main()
