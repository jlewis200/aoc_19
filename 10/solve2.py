#!/usr/bin/env python3

from math import gcd, pi, atan2
from collections import deque
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
    asteroids.remove(max_asteroid)
    target_asteroid = laser(asteroids, max_asteroid)
    return target_asteroid.x * 100 + target_asteroid.y


def laser(asteroids, central_asteroid):
    angles = deque(get_angles(asteroids, central_asteroid))
    laser_count = 0

    previous_delta = None
    while laser_count < 200:

        asteroid, delta = angles.popleft()
        if asteroid not in asteroids or delta == previous_delta:
            continue

        previous_delta = delta
        next_asteroid = find_next_asteroid(asteroids, central_asteroid, delta)
        asteroids.remove(next_asteroid)

        if asteroid != next_asteroid:
            angles.append((asteroid, delta))

        laser_count += 1

    return next_asteroid


def get_angles(asteroids, central_asteroid):
    angles = []

    for asteroid in asteroids:
        delta = (asteroid - central_asteroid).gcd_reduce()
        angle = pi - atan2(delta.x, delta.y)
        angles.append((angle, asteroid, delta))

    angles = sorted(angles, key=lambda x: x[0])
    return deque([(asteroid, delta) for _, asteroid, delta in angles])


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
    main("test_1.txt", 802)
    main("input.txt")
