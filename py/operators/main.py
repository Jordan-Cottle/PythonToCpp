def main() -> int:

    print("7 + 11: ", 7 + 11)
    print("7 - 11: ", 7 - 11)
    print("7 * 11: ", 7 * 11)
    print("4.5 / 2: ", 4.5 / 2)
    print("7 // 3: ", 7 // 3)
    print("3 % 2: ", 3 % 2)

    a = 1 << 2
    print("1 << 2: ", a)
    b = 8 >> 2
    print("8 >> 2: ", b)
    c = 7 ^ 2
    print("7 ^ 2: ", c)
    d = 3 & 2
    print("3 & 2: ", d)
    e = 5 | 2
    print("5 | 2: ", e)

    t = True
    f = False

    # Break down of operations here is only required
    # Due to how std::cout << and these operators interact

    f = t and f
    print("t && f: ", f)
    t = t and t
    print("t && t: ", t)

    t = t or f
    print("t || f: ", t)

    f = f or f
    print("f || f: ", f)

    f = t and t and f
    print("t && t && f: ", f)

    return 0