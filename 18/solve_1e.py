#!/usr/bin/env python3

from string import ascii_lowercase
from collections import deque
import heapq
from pprint import pprint
import numpy as np


class VectorTuple(tuple):
    """
    This class replicates vectorized operations of numpy arrays, with the
    advantage that it's hashable.
    """

    def __new__(cls, *args):
        if len(args) == 1 and not isinstance(args[0], tuple):
            args = args[0]
        return tuple.__new__(VectorTuple, args)

    def __add__(self, other):
        return VectorTuple(
            self_element + other_element
            for self_element, other_element in zip(self, other)
        )

    def __sub__(self, other):
        return VectorTuple(
            self_element - other_element
            for self_element, other_element in zip(self, other)
        )

    def __mul__(self, other):
        return VectorTuple(
            self_element * other_element
            for self_element, other_element in zip(self, other)
        )

    def __truediv__(self, other):
        return VectorTuple(
            self_element / other_element
            for self_element, other_element in zip(self, other)
        )

    def __mod__(self, other):
        return VectorTuple(
            self_element % other_element
            for self_element, other_element in zip(self, other)
        )

    def within_range(self, *ranges):
        return all(element in range_ for element, range_ in zip(self, ranges))

    def orthogonals(self, board):
        """
        Generate E, N, W, S adjacencies.
        """
        for delta in (
            VectorTuple(0, 1),
            VectorTuple(-1, 0),
            VectorTuple(0, -1),
            VectorTuple(1, 0),
        ):
            next_pos = self + delta
            if next_pos.within_range(range(board.shape[0]), range(board.shape[1])):
                yield next_pos

    def diagonals(self, board):
        """
        Generate NE, NW, SW, SE adjacencies.
        """
        for delta in (
            VectorTuple(-1, 1),
            VectorTuple(-1, -1),
            VectorTuple(1, -1),
            VectorTuple(1, 1),
        ):
            next_pos = self + delta
            if next_pos.within_range(range(board.shape[0]), range(board.shape[1])):
                yield next_pos


def solve(board):
    distance_matrix = get_shortest_path_matrix(board)
    dependencies = get_dependencies(board)

    queue = []
    heapq.heappush(queue, (0, 0, 0))

    total_keys = set(range(distance_matrix.shape[0]))
    total_keys = sum(2**key for key in total_keys)

    dependencies_ = [None] * distance_matrix.shape[0]
    for key, deps in dependencies.items():
        deps_ = total_keys
        for dep in deps:
            deps_ ^= 1 << dep
        dependencies_[key] = deps_

    dependencies = dependencies_

    visited = set()
    keys = 0

    while keys != total_keys:
        length, coord, keys = heapq.heappop(queue)

        visited.add((coord, keys))

        keys |= 1 << coord

        for adjacency in range(distance_matrix.shape[0]):

            if (1 << adjacency) & keys != 0:
                continue

            coord_id = (adjacency, keys)

            if coord_id in visited:
                continue

            if dependencies[adjacency] | keys == total_keys:
                heapq.heappush(
                    queue, (length + distance_matrix[coord, adjacency], adjacency, keys)
                )

    print(length)
    return length


def get_char_map(board):
    """
    Map '@' symbol and characters a-z to 0-26
    """
    chars = sorted(set(ascii_lowercase) & set(np.unique(board)))
    chars.insert(0, "@")
    return {char: value for value, char in enumerate(chars)}


def get_dependencies(board):
    """
    Build a map of key to dependencies by tracking doors encountered along the
    path to every key.
    """
    char_map = get_char_map(board)
    coord = VectorTuple(*np.argwhere(board == "@")[0])
    queue = deque([(coord, set())])
    visited = set()
    dependencies = {}

    while len(queue) > 0:
        coord, doors = queue.popleft()
        visited.add(coord)

        if board[coord].islower() and board[coord] not in dependencies:
            dependencies[char_map[board[coord]]] = doors

        for adjacency in coord.orthogonals(board):

            if adjacency in visited:
                continue

            if board[adjacency] != "#":
                if board[adjacency].isupper():
                    doors = doors | {char_map[board[adjacency].lower()]}

                queue.append((adjacency, doors))

    return dependencies


def get_shortest_path_matrix(board):
    """
    Generate all pair shortest path matrix.
    """
    char_map = get_char_map(board)
    matrix_size = (len(char_map),) * 2
    matrix = np.zeros(matrix_size, dtype=np.uint16)  # matrix[src, dst]

    for src, src_value in char_map.items():
        shortest_paths = get_single_source_all_dest_shortest_paths(board, src)

        for dst, length in shortest_paths.items():
            matrix[src_value, char_map[dst]] = length

    return matrix


def get_single_source_all_dest_shortest_paths(board, source):
    """
    Build single source all destination distance map.
    """
    coord = VectorTuple(*np.argwhere(board == source)[0])
    length = 0
    queue = deque([(coord, length)])
    visited = set()
    lengths = {}

    while len(queue) > 0:
        coord, length = queue.popleft()
        visited.add(coord)

        if board[coord] in ascii_lowercase + "@" and board[coord] not in lengths:
            lengths[board[coord]] = length

        for adjacency in coord.orthogonals(board):

            if adjacency in visited:
                continue

            if board[adjacency] != "#":
                queue.append((adjacency, length + 1))

    return lengths


def parse(lines):
    lines = [list(line.strip()) for line in lines]
    return np.array(lines)


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename):
    """
    86
    132
    136
    81
    solving
    3646
    3646

    real	23m10.583s
    user	22m56.562s
    sys	0m14.266s
    """
    assert solve(parse(read_file("test_0.txt"))) == 86
    assert solve(parse(read_file("test_1.txt"))) == 132
    # assert solve(parse(read_file("test_2.txt"))) == 136
    assert solve(parse(read_file("test_3.txt"))) == 81
    print("solving")
    # print(solve(parse(read_file(filename))))


if __name__ == "__main__":
    main("input.txt")
