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
    total_keys = 2 ** distance_matrix.shape[0] - 1
    dependencies = get_dependencies(board, total_keys)

    queue = initialize_queue()
    visited = set()
    pending_visit = set()
    keys = 0

    while keys != total_keys and len(queue) > 0:
        length, *state = heapq.heappop(queue)
        visited.add(tuple(state))
        *robot_positions, keys = state
        keys = update_keys(keys, robot_positions)

        # enumerate each of the robots
        for idx, robot_position in enumerate(robot_positions):

            # enumerate adjacencies for a robot
            for adjacency in range(distance_matrix.shape[0]):

                # skip if we already have the key for the adjacency
                if ((1 << adjacency) & keys) != 0:
                    continue

                # skip if there is no path to the adjacency
                if distance_matrix[robot_position, adjacency] == INF:
                    continue

                adjacency_ = robot_positions.copy()
                adjacency_[idx] = adjacency
                state = tuple(adjacency_) + (keys,)

                if state in visited:
                    continue

                # proceed if we have all of the keys required to travel to the adjacency
                if dependencies[adjacency] | keys == total_keys:
                    next_state = (
                        length + distance_matrix[robot_position, adjacency],
                        *state,
                    )

                    # proceed if the next state is not already pending
                    if next_state not in pending_visit:
                        pending_visit.add(next_state)
                        heapq.heappush(queue, next_state)

    print(length)
    return length


def update_keys(keys, robot_positions):
    # set key bits for each current robot position
    for robot_position in robot_positions:
        keys |= 1 << robot_position

    return keys


def initialize_queue():
    queue = []
    length = 0
    initial_coord = (0, 1, 2, 3)
    keys = 0
    heapq.heappush(queue, (length,) + initial_coord + (keys,))
    return queue


def bit_vectorize_dependencies(dependencies, total_keys):
    """
    Create a list of bitvectors to encode the dependencies of each key.

    ex:
                                  key_0 ------|
                                  key_2 ----v v
        vectorized_dependencies[key_3]:  0b1010
        this means `key_3` requires key_0 and key_2
    """
    vectorized_dependencies = [total_keys] * total_keys.bit_length()

    for key, key_dependencies in dependencies.items():
        vectorized_key_dependencies = total_keys

        for dep in key_dependencies:
            vectorized_key_dependencies ^= 1 << dep

        vectorized_dependencies[key] = vectorized_key_dependencies

    return vectorized_dependencies


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


def get_dependencies(board, total_keys):
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

    return bit_vectorize_dependencies(dependencies, total_keys)


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
