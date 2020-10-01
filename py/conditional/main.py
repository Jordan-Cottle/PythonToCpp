def main() -> int:
    age = -1

    if age < 0:
        print("That's not possible")
    elif age >= 60:
        print("If you're lucky, you can retire")
    elif age >= 21:
        print("You're allowed to be an adult")
    elif age >= 18:
        print("You're an adult")
    else:
        print("You're just a child")

    return 0