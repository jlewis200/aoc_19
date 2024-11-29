#!/usr/bin/env python3


def solve(weights):
    return sum(get_fuel(weight) for weight in weights)


def get_fuel(weight):
    return (weight // 3) - 2


def parse(lines):
    return list(map(int, lines))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename, expected=None):
    result = solve(parse(read_file(filename)))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    assert solve([12, 14, 1969, 100756]) == sum([2, 2, 654, 33583])
    main("input.txt")
