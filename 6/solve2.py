#!/usr/bin/env python3

import networkx as nx


def solve(orbits):
    graph = nx.Graph(orbits)
    return nx.shortest_path_length(graph, "YOU", "SAN") - 2


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
    main("test2.txt", 4)
    main("input.txt")
