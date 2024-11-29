#!/usr/bin/env python3


def solve(weights):
    cache = {}
    return sum(get_fuel(weight, cache) for weight in weights)


def get_fuel(weight, cache):
    try:
        return cache[weight]

    except KeyError:
        fuel = (weight // 3) - 2

        if fuel < 0:
            return 0

        return fuel + get_fuel(fuel, cache)


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
    assert solve([14, 1969, 100756]) == sum([2, 966, 50346])
    main("input.txt")
