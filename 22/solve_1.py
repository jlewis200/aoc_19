#!/usr/bin/env python3


def solve(actions, deck_size=10007):
    deck = list(range(deck_size))

    for function, arg in actions:
        deck = function(deck, arg)

    return deck


def stack(deck, _):
    return deck[::-1]


def cut(deck, position):
    return deck[position:] + deck[:position]


def increment(deck, interval):
    result = [None] * len(deck)

    for src_idx, card in enumerate(deck):
        dst_idx = (src_idx * interval) % len(deck)
        result[dst_idx] = card

    return result


def parse(lines):
    parsed = []

    for line in lines:
        line = line.strip()

        if "stack" in line:
            parsed.append((stack, None))

        elif "increment" in line:
            parsed.append((increment, int(line.split()[-1])))

        elif "cut" in line:
            parsed.append((cut, int(line.split()[-1])))

    return parsed


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename):
    assert solve(parse(read_file("test_0.txt")), deck_size=10) == [
        0,
        3,
        6,
        9,
        2,
        5,
        8,
        1,
        4,
        7,
    ]
    assert solve(parse(read_file("test_1.txt")), deck_size=10) == [
        3,
        0,
        7,
        4,
        1,
        8,
        5,
        2,
        9,
        6,
    ]
    assert solve(parse(read_file("test_2.txt")), deck_size=10) == [
        6,
        3,
        0,
        7,
        4,
        1,
        8,
        5,
        2,
        9,
    ]
    assert solve(parse(read_file("test_3.txt")), deck_size=10) == [
        9,
        2,
        5,
        8,
        1,
        4,
        7,
        0,
        3,
        6,
    ]
    print(solve(parse(read_file(filename))).index(2019))


if __name__ == "__main__":
    main("input.txt")
