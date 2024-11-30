#!/usr/bin/env python3

from math import gcd
import numpy as np


class Coord:

    y_range = None
    x_range = None

    def __init__(self, y, x):
        self.y = int(y)
        self.x = int(x)
        self._hash = None

    def __add__(self, other):
        return Coord(self.y + other.y, self.x + other.x)

    def __sub__(self, other):
        return Coord(self.y - other.y, self.x - other.x)

    def __mul__(self, other):
        return Coord(self.y * other, self.x * other)

    def __hash__(self):
        if self._hash is None:
            self._hash = (1000003 * self.x) ^ self.y
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Coord):
            return False
        return self.y == other.y and self.x == other.x

    def __repr__(self):
        return f"{self.y}\t{self.x}"

    def gcd_reduce(self):
        """
        Reduce the y/x coord by the greatest common divisor.  Ex:

         2,  2 ->  1,  1
        -3, -9 -> -1, -3
        """
        if self.y == 0 or self.x == 0:
            divisor = max(abs(self.y), abs(self.x), 1)
        else:
            divisor = gcd(self.y, self.x)

        return Coord(self.y // divisor, self.x // divisor)

    @classmethod
    def set_ranges(cls, asteroids):
        y_max = max(asteroid.y for asteroid in asteroids)
        x_max = max(asteroid.x for asteroid in asteroids)
        cls.y_range = range(y_max + 1)
        cls.x_range = range(x_max + 1)

    def valid(self):
        return self.y in self.y_range and self.x in self.x_range


def solve(board):
    asteroids = np.argwhere(board == "#")
    asteroids = {Coord(*asteroid) for asteroid in asteroids}
    Coord.set_ranges(asteroids)
    max_viewable, max_asteroid = get_central_asteroid(asteroids)
    return max_viewable


def get_central_asteroid(asteroids):
    """
    Find the asteroid with the best view of the other asteroids.
    """
    max_viewable = 0
    max_asteroid = None

    for asteroid in asteroids:
        n_viewable = find_viewable(asteroids, asteroid)

        if n_viewable > max_viewable:
            max_viewable = n_viewable
            max_asteroid = asteroid

    return max_viewable, max_asteroid


def find_viewable(asteroids, asteroid):
    """
    Find the number of asteroids visible from the specified asteroid.
    """
    n_viewable = 0

    for asteroid_1 in asteroids:
        if asteroid != asteroid_1 and not blocked(asteroids, asteroid, asteroid_1):
            n_viewable += 1

    return n_viewable


def blocked(asteroids, asteroid, asteroid_1):
    """
    Check if the path between two asteroids is blocked.  Travel from one
    asteroid to the other.  If the next asteroid encountered is the other
    asteroid, the path is not blocked.
    """
    delta = (asteroid_1 - asteroid).gcd_reduce()

    if asteroid_1 == find_next_asteroid(asteroids, asteroid, delta):
        return False

    return True


def find_next_asteroid(asteroids, coord, delta):
    """
    Find the next asteroid from coord with travelling along delta direction.
    """
    while coord.valid():
        coord += delta

        if coord in asteroids:
            return coord


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
