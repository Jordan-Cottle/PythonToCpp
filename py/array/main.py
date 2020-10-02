# This function is for testing tuples
def fibonacci(count: int) -> int:
    fib = (1, 0)

    i = 0
    sum = 0
    while i < count:
        i += 1

        sum = fib[0] + fib[1]

        print(sum)

        fib[0] = fib[1]
        fib[1] = sum

    return sum


# This function is for testing lists
def primes(up_to: int) -> None:

    prime = [True]
    j = 0
    while j < up_to:
        prime.append(True)
        j += 1

    p = 2
    while p * p <= up_to:
        if prime[p]:
            j = p * 2
            while j <= up_to:
                prime[j] = False
                j += p
        p += 1

    prime[0] = False
    prime[1] = False

    j = 2
    while j <= up_to:
        if prime[j]:
            print(j)
        j += 1


def main() -> int:
    n = 10
    print("First ", n, " fibonacci numbers:")
    n = fibonacci(n)

    print("All primes up to ", n)
    primes(n)
