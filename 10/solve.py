#!/usr/bin/env python3

from math import gcd
import numpy as np


def solve(board):
    asteroids = np.argwhere(board == "#")
    asteroids = {tuple(asteroid) for asteroid in asteroids}
    max_viewable, max_asteroid = get_central_asteroid(asteroids)
    return max_viewable


def get_central_asteroid(asteroids):
    max_viewable = 0
    max_asteroid = None

    for asteroid in asteroids:
        n_viewable = find_viewable(asteroids, asteroid)

        if n_viewable > max_viewable:
            max_viewable = n_viewable
            max_asteroid = asteroid

    return max_viewable, max_asteroid


def find_viewable(asteroids, asteroid):
    n_viewable = 0

    for asteroid_1 in asteroids:

        if asteroid == asteroid_1:
            continue

        if unblocked(asteroids, asteroid, asteroid_1):
            n_viewable += 1

    return n_viewable


def get_ranges(asteroids):
    y_max = max(y for y, _ in asteroids)
    x_max = max(x for _, x in asteroids)
    return range(y_max + 1), range(x_max + 1)


def reduce(dy, dx):
    """
    Reduce the deltas by the greatest common divisor.  Ex:

     2,  2 ->  1,  1
    -3, -9 -> -1, -3
    """
    if dy == 0 or dx == 0:
        divisor = max(abs(dy), abs(dx), 1)
    else:
        divisor = gcd(dy, dx)

    return dy // divisor, dx // divisor


def unblocked(asteroids, asteroid, asteroid_1):
    y_range, x_range = get_ranges(asteroids)

    dy, dx = asteroid_1[0] - asteroid[0], asteroid_1[1] - asteroid[1]
    dy, dx = reduce(dy, dx)

    for modifier in (1, -1):
        y, x = asteroid
        dy, dx = dy * modifier, dx * modifier

        while valid_coord(y, x, y_range, x_range):
            y, x = y + dy, x + dx

            if (y, x) == asteroid_1:
                return True

            elif (y, x) in asteroids:
                return False


def valid_coord(y, x, y_range, x_range):
    return y in y_range and x in x_range


def parse(lines):
    return np.array(list(list(line.strip()) for line in lines))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename, expected=None):
    result = solve(parse(read_file(filename)))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test_0.txt", 8)
    main("input.txt")
