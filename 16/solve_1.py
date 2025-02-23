#!/usr/bin/env python3

import numpy as np


def solve(signal, pattern=[0, 1, 0, -1], phases=100):
    pattern = pattern_generator(pattern, len(signal))
    signal = np.array(signal)

    for _ in range(phases):
        signal = abs(pattern @ signal) % 10

    return "".join(map(str, signal[:8]))


def pattern_generator(pattern, length):
    pattern_matrix = []

    for row in range(1, 1 + length):
        row_pattern = np.repeat(pattern, row)
        tile_count = int(np.ceil((length + 1) / row_pattern.shape[0]))
        row_pattern = np.tile(row_pattern, tile_count)
        row_pattern = row_pattern[1 : 1 + length]
        pattern_matrix.append(row_pattern)

    return np.array(pattern_matrix)


def parse(line):
    return list(map(int, list(line.strip())))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename):
    assert solve(parse("12345678"), phases=4) == "01029498"
    assert solve(parse("80871224585914546619083218645595")) == "24176176"
    assert solve(parse("19617804207202209144916044189917")) == "73745418"
    assert solve(parse("69317163492948606335995924319873")) == "52432133"
    print(solve(parse(read_file(filename))))


if __name__ == "__main__":
    main("input.txt")
