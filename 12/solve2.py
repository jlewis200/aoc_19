#!/usr/bin/env python3

from re import fullmatch
from math import lcm
import numpy as np


def solve(positions, steps):
    """
    Get the cycle lengths for each dimension.  The least common multiple will
    be the first time every dimension state is exactly the same as the initial.
    Because it is cyclic, the first possible cycle will occur at the initial
    state.
    """
    lengths = []

    for idx in range(3):
        lengths.append(cycle_length(positions.copy(), steps, idx))

    return lcm(*lengths)


def cycle_length(positions, steps, idx):
    """
    Assume that if two consective x/y/z positions in isolation completely define
    a state.  I don't think this is correct in general, but it works for this
    input.  A cycle is detected when a previous state results in the same next
    state.  Return the number of steps requried to induce the cycle.
    """
    velocities = np.zeros_like(positions)
    cache = set()
    prev = tuple(positions[:, idx])
    prev_cache_size = len(cache)

    for _ in range(steps):
        step(positions, velocities)
        current = tuple(positions[:, idx])
        cache.add((prev, current))

        if len(cache) == prev_cache_size:
            return len(cache)

        prev_cache_size = len(cache)
        prev = current

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
    main("test.txt", 10000000000, expected=2772)
    main("test_1.txt", 1000000000000, expected=4686774924)
    main("input.txt", 10000000000000000000000)
