#!/usr/bin/env python3

from string import ascii_lowercase
from collections import deque
import heapq
from pprint import pprint
import numpy as np

INF = 2**16 - 1


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
    keys = sum(2**idx for idx in range(4))
    heapq.heappush(queue, (0, 0, 1, 2, 3, keys))

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

    while keys != total_keys and len(queue) > 0:
        # pprint(queue)
        length, *coord, keys = heapq.heappop(queue)
        coord = tuple(coord)
        # coord_0, coord_1, coord_2, coord_3 = coord
        visited.add((coord, keys))

        for coord_ in coord:
            keys |= 1 << coord_

        for idx, coord_ in enumerate(coord):

            for adjacency in range(distance_matrix.shape[0]):

                if (1 << adjacency) & keys != 0:
                    continue

                if distance_matrix[coord_, adjacency] == INF:
                    continue

                adjacency_ = list(coord)
                adjacency_[idx] = adjacency
                adjacency_ = tuple(adjacency_)

                coord_id = (adjacency_, keys)

                if coord_id in visited:
                    continue

                if dependencies[adjacency] | keys == total_keys:
                    heapq.heappush(
                        queue,
                        (
                            length + distance_matrix[coord_, adjacency],
                            *adjacency_,
                            keys,
                        ),
                    )

    print(length)
    return length


def get_char_map(board):
    """
    Map '0', '1', '2', '3' and characters a-z to 0-29
    0:0
    1:1
    2:2
    3:3
    a:4
    b:5
    ...
    z:29
    """
    chars = sorted(set(ascii_lowercase) & set(np.unique(board)))
    chars = ["0", "1", "2", "3"] + chars
    return {char: value for value, char in enumerate(chars)}


def get_dependencies(board):
    """
    Build a map of key to dependencies by tracking doors encountered along the
    path to every key.
    """
    char_map = get_char_map(board)
    visited = set()
    dependencies = {}

    for char in ["0", "1", "2", "3"]:
        coord = VectorTuple(*np.argwhere(board == char)[0])
        queue = deque([(coord, set())])

        while len(queue) > 0:
            coord, doors = queue.popleft()
            doors = doors.copy()
            visited.add(coord)

            if board[coord].islower() and board[coord] not in dependencies:
                dependencies[char_map[board[coord]]] = doors

            for adjacency in coord.orthogonals(board):

                if adjacency in visited:
                    continue

                if board[adjacency] != "#":
                    doors_ = doors.copy()

                    if board[adjacency].isupper():
                        doors_ = doors | {char_map[board[adjacency].lower()]}

                    queue.appendleft((adjacency, doors_))

    return dependencies


def get_shortest_path_matrix(board):
    """
    Generate all pair shortest path matrix.
    """
    char_map = get_char_map(board)
    matrix_size = (len(char_map),) * 2
    matrix = np.full(matrix_size, INF, dtype=np.uint16)  # matrix[src, dst]

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

        if board[coord] in ascii_lowercase + "0123" and board[coord] not in lengths:
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
    assert solve(parse(read_file("test_4.txt"))) == 8
    assert solve(parse(read_file("test_5.txt"))) == 24
    assert solve(parse(read_file("test_6.txt"))) == 32
    assert solve(parse(read_file("test_7.txt"))) == 72
    print("solving")
    print(solve(parse(read_file(filename))))


if __name__ == "__main__":
    main("input2.txt")
