#!/usr/bin/env python3

from re import fullmatch
import numpy as np


def solve(positions, steps):
    velocities = np.zeros_like(positions)

    for _ in range(steps):
        step(positions, velocities)

    return get_energy(positions, velocities)


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
    main("test.txt", 10, expected=179)
    main("test_1.txt", 100, expected=1940)
    main("input.txt", 1000)
