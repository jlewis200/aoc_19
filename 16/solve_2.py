#!/usr/bin/env python3

import numpy as np


def solve(start_idx, signal, phases=100):
    """
    next signal = pattern_matrix @ signal

    pattern matrix:

    1  0 -1  0  1  0 -1  0
       1  1  0  0 -1 -1  0
          1  1  1  0  0  0
             1  1  1  1  0  <- midpoint
                1  1  1  1
                   1  1  1
                      1  1
                         1

    Two things make this problem easier to solve than the naive case.

    #1:  The 'pattern matrix' of 0, 1, 0, -1 tends to form a triangular matrix.
         Every non-zero element is on or above the upper diagonal.
         This means the element at position idx only depends on the values of
         the signal at positions >= idx

    #2:  After the midpoint, the pattern matrix is triangular with only ones.
         This means each element of the next signal in this region can be
         calucated using a single pass starting from the end of the signal
         going backwards.

    Because we're only interested in the digits starting from an index close
    to the end of the signal, we can apply the technique from point #2 and halt
    the phase once we process the target digits per point #1.
    """
    signal = get_reversed_signal_section(start_idx, signal)

    for _ in range(phases):
        signal = perform_phase(signal)

    return "".join(map(str, signal[-8:][::-1]))


def perform_phase(signal):
    """
    Perform a single phase.
    """
    next_signal = []
    value = 0

    for element in signal:
        value += element
        value %= 10
        next_signal.append(value)

    return next_signal


def get_reversed_signal_section(start_idx, signal):
    """
    Get the end portion of the signal after repeating
    """
    signal_length = len(signal) * 10_000
    end_index = signal_length - start_idx
    signal = signal[::-1]
    whole_repeats = end_index // len(signal)
    single_elements = end_index % len(signal)
    return (signal * whole_repeats) + signal[:single_elements]


def parse(line):
    start_idx = int(line[:7])
    signal = list(map(int, list(line.strip())))
    return start_idx, signal


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename):
    assert solve(*parse("03036732577212944063491565474664")) == "84462026"
    assert solve(*parse("02935109699940807407585447034323")) == "78725270"
    assert solve(*parse("03081770884921959731165446850517")) == "53553731"
    print(solve(*parse(read_file(filename))))


if __name__ == "__main__":
    main("input.txt")
