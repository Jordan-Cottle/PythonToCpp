def main() -> int:
    i = 0

    while True:
        i += 1

        if i % 15 == 0:
            print("fizzbuzz")
            break

        if i % 3 == 0:
            print("fizz")
            continue

        if i % 5 == 0:
            print("buzz")
            continue

        print(i)

    return 0
