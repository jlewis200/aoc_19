#!/usr/bin/env python3

import networkx as nx


def solve(orbits):
    graph = nx.DiGraph(orbits).reverse()
    total = 0

    for _, length in nx.single_target_shortest_path_length(graph, "COM"):
        total += length

    return total


def parse(lines):
    return list(map(lambda x: x.strip().split(")"), lines))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename, expected=None):
    result = solve(parse(read_file(filename)))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test.txt", 42)
    main("input.txt")
