class A:
    name: str
    value: int

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def hello(self) -> None:
        print(self.name)

    def add(self, num: int) -> int:
        self.value += num

        return self.value


def main() -> int:
    a = A("Hello world", 11)

    a.hello()

    a.add(7)

    print(a.value)
