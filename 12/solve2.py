#!/usr/bin/env python3

from re import fullmatch
from math import lcm
import numpy as np


def solve(positions, steps):
    """
    The position and velocities of each dimension are independent of the other
    dimensions.  The overall cycle will be a multiple of the per-dimension
    cycles.  The cycles are found by treating the per-dimension positions and
    velocities as a state and adding to a set.  The loop is terminated when all
    dimension sets no longer grows.  The least common multiple will of the
    per-dimension set lengths will be the first time every dimension state is
    exactly the same as the initial.
    """
    velocities = np.zeros_like(positions)
    x_cache = set()
    y_cache = set()
    z_cache = set()
    x_vector = tuple(positions[:, 0]) + tuple(velocities[:, 0])
    y_vector = tuple(positions[:, 1]) + tuple(velocities[:, 1])
    z_vector = tuple(positions[:, 2]) + tuple(velocities[:, 2])

    while x_vector not in x_cache or y_vector not in y_cache or z_vector not in z_cache:
        step(positions, velocities)
        x_cache.add(x_vector)
        y_cache.add(y_vector)
        z_cache.add(z_vector)
        x_vector = tuple(positions[:, 0]) + tuple(velocities[:, 0])
        y_vector = tuple(positions[:, 1]) + tuple(velocities[:, 1])
        z_vector = tuple(positions[:, 2]) + tuple(velocities[:, 2])

    return lcm(len(x_cache), len(y_cache), len(z_cache))


def step(positions, velocities):
    velocities += get_delta_velocities(positions)
    positions += velocities


def get_delta_velocities(positions):
    delta_velocities = []

    for position in positions:
        delta = (positions > position).sum(axis=0) - (positions < position).sum(axis=0)
        delta_velocities.append(delta)

    return np.array(delta_velocities)


def get_energy(positions, velocities):
    return abs(positions).sum(axis=1) @ abs(velocities).sum(axis=1)


def parse(lines):
    positions = []

    for line in lines:
        match = fullmatch("<x=(?P<x>.+), y=(?P<y>.+), z=(?P<z>.+)>", line.strip())
        positions.append(
            (
                int(match.group("x")),
                int(match.group("y")),
                int(match.group("z")),
            )
        )
    return np.array(positions)


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename, *args, expected=None):
    result = solve(parse(read_file(filename)), *args)
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test.txt", 10000000000, expected=2772)
    main("test_1.txt", 1000000000000, expected=4686774924)
    main("input.txt", 10000000000000000000000)
