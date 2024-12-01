#!/usr/bin/env python3

from re import fullmatch
from math import ceil
import networkx as nx


def solve(reactions):
    nodes, edges = get_edges(reactions)
    graph = nx.DiGraph(edges)
    nx.set_node_attributes(graph, nodes, "quantity")
    graph = graph.reverse()

    for node in nx.topological_sort(graph):
        required_output_quantity = get_required_output_quantity(graph, node)
        multiplier = ceil(required_output_quantity / graph.nodes[node]["quantity"])
        graph.nodes[node]["quantity"] *= multiplier
        increase_production(graph, node, multiplier)

    return graph.nodes["ORE"]["quantity"]


def increase_production(graph, node, multiplier):
    for *_, data in graph.out_edges(node, data=True):
        data["quantity_required"] *= multiplier


def get_required_output_quantity(graph, node):
    required_output_quantity = 0

    for *_, data in graph.in_edges(node, data=True):
        required_output_quantity += data["quantity_required"]

    required_output_quantity = max(1, required_output_quantity)

    return required_output_quantity


def get_edges(reactions):
    edges = []
    nodes = {"ORE": 1}

    for srcs, dst in reactions:
        dst_value, dst_name = dst
        nodes[dst_name] = dst_value

        for src in srcs:
            src_value, src_name = src
            edges.append((src_name, dst_name, {"quantity_required": src_value}))

    return nodes, edges


def parse(lines):
    reactions = []

    for line in lines:
        match = fullmatch("(?P<inputs>.+) => (?P<output>.+)", line.strip())
        reactions.append(
            (
                tuple(
                    parse_chemical(input_)
                    for input_ in match.group("inputs").split(",")
                ),
                parse_chemical(match.group("output")),
            )
        )

    return reactions


def parse_chemical(chemical):
    match = fullmatch("(?P<quantity>\d+) (?P<name>.+)", chemical.strip())
    return int(match.group("quantity")), match.group("name")


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename, expected=None):
    result = solve(parse(read_file(filename)))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test_0.txt", 165)
    main("test_1.txt", 13312)
    main("test_2.txt", 180697)
    main("test_3.txt", 2210736)
    main("input.txt")
