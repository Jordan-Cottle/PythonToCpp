def main() -> int:
    age = 17

    teen = 13
    adult = 18
    real_adult = 21

    print("teenager: ", teen <= age <= adult)
    print("adult: ", adult <= age <= real_adult)
    print("real adult: ", real_adult <= age)

    return 0
