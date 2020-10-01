def exception_test() -> int:
    try:
        raise RuntimeError("This is a test")
    except Exception as e:
        print("ERROR: An error has been encountered")
        return 1

    return 0


def main() -> int:
    error_code = exception_test()

    if error_code == 1:
        print("Success! The error was detected")
    else:
        print("Fail! The error was not detected")