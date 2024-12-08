#!/usr/bin/env python3

from collections import deque, defaultdict
from itertools import repeat, chain
from time import sleep
import numpy as np
import networkx as nx


class AddressModes:
    POSITION_MODE = 0
    IMMEDIATE_MODE = 1
    RELATIVE_MODE = 2


class Opcode:
    ADD = 1
    MULT = 2
    INPUT = 3
    OUTPUT = 4
    JUMP_NOT_ZERO = 5
    JUMP_ZERO = 6
    LESS_THAN = 7
    EQUAL = 8
    ADJUST_RELATIVE_BASE = 9
    TERMINATE = 99


class Interpreter:

    def __init__(self, program):
        self.ip = 0
        self.program = self.convert_program(program)
        self.input_queue = deque()
        self.output_queue = deque()
        self.state = "initialized"
        self.relative_base = 0

    def __str__(self):
        string = f"ip:\t{self.ip}\n"
        string += "\t" + "\t".join("0123456789") + "\n"
        string += "-" * 90

        for idx, value in enumerate(self.program):

            if idx % 10 == 0:
                string += f"\n{idx}:\t{value}"
            else:
                string += f"\t{value}"

        return string

    @staticmethod
    def convert_program(program):
        """
        Convert from list to dictionary.
        """
        program_dict = defaultdict(lambda: 0)

        for idx, value in enumerate(program):
            program_dict[idx] = value

        return program_dict

    def run(self, input_queue):
        self.state = "running"
        self.input_queue.extend(input_queue)

        while self.state not in ("terminated", "input_blocking"):
            self.process_instruction()

        return self.output_queue

    def add(self):
        arg_0, arg_1, p_destination = self.get_args(arg_types=("in", "in", "out"))
        self.program[p_destination] = arg_0 + arg_1

    def mult(self):
        arg_0, arg_1, p_destination = self.get_args(arg_types=("in", "in", "out"))
        self.program[p_destination] = arg_0 * arg_1

    def input(self):
        try:
            input_value = self.input_queue.popleft()
        except IndexError:
            self.state = "input_blocking"
            return

        p_destination = self.get_args(arg_types=("out",))
        self.program[p_destination] = input_value

    def output(self):
        arg = self.get_args(arg_types=("in",))
        self.output_queue.append(arg)

    def jump_not_zero(self):
        arg, destination = self.get_args(arg_types=("in", "in"))
        if arg != 0:
            self.ip = destination

    def jump_zero(self):
        arg, destination = self.get_args(arg_types=("in", "in"))
        if arg == 0:
            self.ip = destination

    def less_than(self):
        arg_0, arg_1, p_destination = self.get_args(arg_types=("in", "in", "out"))
        if arg_0 < arg_1:
            self.program[p_destination] = 1
        else:
            self.program[p_destination] = 0

    def equal(self):
        arg_0, arg_1, p_destination = self.get_args(arg_types=("in", "in", "out"))
        if arg_0 == arg_1:
            self.program[p_destination] = 1
        else:
            self.program[p_destination] = 0

    def adjust_relative_base(self):
        arg = self.get_args(arg_types=("in",))
        self.relative_base += arg

    def terminate(self):
        self.state = "terminated"

    def error(self):
        print(self)
        raise ValueError

    def process_instruction(self):
        match self.get_opcode(self.program[self.ip]):

            case Opcode.ADD:
                self.add()

            case Opcode.MULT:
                self.mult()

            case Opcode.INPUT:
                self.input()

            case Opcode.OUTPUT:
                self.output()

            case Opcode.JUMP_NOT_ZERO:
                self.jump_not_zero()

            case Opcode.JUMP_ZERO:
                self.jump_zero()

            case Opcode.LESS_THAN:
                self.less_than()

            case Opcode.EQUAL:
                self.equal()

            case Opcode.ADJUST_RELATIVE_BASE:
                self.adjust_relative_base()

            case Opcode.TERMINATE:
                self.terminate()

            case _:
                self.error()

    @staticmethod
    def get_opcode(instruction):
        return instruction % 100

    @staticmethod
    def get_parameter_modes(instruction):
        """
        Get the modes of an opcode's parameter.  Leading zeros are omitted from the
        opcode, so this generator will return 0s indefinitely.
        """
        modes = str(instruction // 100)
        modes = map(int, reversed(modes))
        yield from chain(modes, repeat(AddressModes.POSITION_MODE))

    def get_arg(self, mode):
        match mode:

            case AddressModes.POSITION_MODE:
                return self.program[self.program[self.ip]]

            case AddressModes.IMMEDIATE_MODE:
                return self.program[self.ip]

            case AddressModes.RELATIVE_MODE:
                return self.program[self.relative_base + self.program[self.ip]]

    def get_out_arg(self, parameter_mode):
        arg = self.get_arg(AddressModes.IMMEDIATE_MODE)

        if parameter_mode == AddressModes.RELATIVE_MODE:
            arg += self.relative_base

        return arg

    def get_args(self, arg_types):
        """
        Arg types:
            in: possibly dereferenced
            out: never dereferenced

        In parameters are dereferenced if parameter mode is 0 (positions mode),
        and the raw value is returned for mode 1 (immediate mode).

        Out parameters are not dereferenced.
        """
        assert isinstance(arg_types, (tuple, list))

        instruction = self.program[self.ip]
        args = []
        p_destination = None
        parameter_modes = self.get_parameter_modes(self.program[self.ip])

        for arg_type in arg_types:
            self.ip += 1
            parameter_mode = next(parameter_modes)

            if arg_type == "in":
                args.append(self.get_arg(parameter_mode))

            elif arg_type == "out":
                args.append(self.get_out_arg(parameter_mode))

        self.ip += 1

        if len(args) == 1:
            return args.pop()

        return args


class Coord:
    y_range = None
    x_range = None

    def __init__(self, y, x):
        self.y = int(y)
        self.x = int(x)
        self._hash = None

    def __add__(self, other):
        return Coord(self.y + other.y, self.x + other.x)

    def __sub__(self, other):
        return Coord(self.y - other.y, self.x - other.x)

    def __mul__(self, other):
        return Coord(self.y * other, self.x * other)

    def __hash__(self):
        if self._hash is None:
            self._hash = (1000003 * self.x) ^ self.y
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Coord):
            return False
        return self.y == other.y and self.x == other.x

    def __repr__(self):
        return f"{self.y}\t{self.x}"


class Movement:
    north = 1
    south = 2
    west = 3
    east = 4

    inversion_map = {
        north: south,
        south: north,
        west: east,
        east: west,
    }

    delta_map = {
        north: Coord(-1, 0),
        south: Coord(1, 0),
        west: Coord(0, -1),
        east: Coord(0, 1),
    }

    @classmethod
    def invert(cls, direction):
        return cls.inversion_map[direction]

    @classmethod
    def get_delta(cls, direction):
        return cls.delta_map[direction]


class Status:
    wall = 0
    reachable = 1
    target = 2


def solve(program):
    interpreter = Interpreter(program)
    map_searcher = MapSearcher(interpreter)
    map_searcher.build_graph()
    return map_searcher.get_solution_1(), map_searcher.get_solution_2()


class MapSearcher:

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.start = Coord(50, 50)
        self.pos = self.start
        self.graph = nx.DiGraph()
        self.graph.add_node(self.pos, status=Status.reachable)
        self.node_queue = deque()
        self.enqueue_adjacencies()
        self.add_adjacencies()

    def build_graph(self):
        """
        Build a graph through DFS using sensory data from the robot.
        """
        next_node = self.dequeue_node()

        while next_node is not None:
            self.travel(next_node)
            next_node = self.dequeue_node()

    def travel(self, next_node):
        """
        Travel to an unvisited next_node.  If a wall is encountered, undate the
        robot instructions based on the new information and try again.
        """
        input_queue = self.get_action_queue(next_node)

        while len(input_queue) > 0:
            status, attempted_pos = self.step(input_queue.popleft())

            if status == Status.wall:
                input_queue = self.unsuccessful_step(
                    attempted_pos,
                    next_node,
                    input_queue,
                )

            else:
                self.successful_step(attempted_pos)

            print(self.board_str())
            sleep(0.01)

    def step(self, action):
        """
        Take a single step and update graph information.
        """
        status = self.interpreter.run((action,)).popleft()
        attempted_pos = self.pos + Movement.get_delta(action)
        self.graph.nodes[attempted_pos]["status"] = status
        return status, attempted_pos

    def successful_step(self, attempted_pos):
        """
        Handle a successful step by updating the robot position, adding any
        new adjacencies to the node queue, and adding new adjacencies to the
        graph.
        """
        self.pos = attempted_pos
        self.enqueue_adjacencies()
        self.add_adjacencies()

    def unsuccessful_step(self, attempted_pos, next_node, input_queue):
        """
        Handle an unsuccessful step where the robot is blocked by removing all
        edges to the wall.  Get a new action map if the intended destination
        wasn't reached.  If the wall was the intended destination, don't
        update the input queue.
        """
        self.remove_edges(attempted_pos)

        if len(input_queue) > 0:
            input_queue = self.get_action_queue(next_node)

        return input_queue

    def remove_edges(self, node):
        """
        Remove all edges of a node.
        """
        for edge in list(self.graph.in_edges(node)) + list(self.graph.out_edges(node)):
            self.graph.remove_edge(*edge)

    def get_action_queue(self, next_node):
        """
        Return the actions required to reach next node based on the robot's
        current understanding of the area.
        """
        action_queue = deque()
        path = nx.shortest_path(self.graph, self.pos, next_node, weight="weight")

        for edge in np.lib.stride_tricks.sliding_window_view(path, 2):
            action_queue.append(self.graph.edges[edge]["direction"])

        return action_queue

    def add_adjacencies(self):
        """
        Add adjacent nodes/edges to the current position if they don't exist.
        """
        for direction, adjacency in zip(
            self.get_directions(),
            self.generate_adjacencies(),
        ):
            if adjacency not in self.graph.nodes:
                self.graph.add_node(adjacency, status=None)
                self.graph.add_edge(
                    self.pos,
                    adjacency,
                    direction=direction,
                    weight=1,
                )
                self.graph.add_edge(
                    adjacency,
                    self.pos,
                    direction=Movement.invert(direction),
                    weight=1,
                )

    def enqueue_adjacencies(self):
        """
        Add new adjacencies to the node queue.  The adjacencies are added to
        the left to produce a DFS.
        """
        for node in self.generate_adjacencies():
            if node not in self.graph.nodes:
                self.node_queue.appendleft(node)

    def dequeue_node(self):
        """
        Return the first unvisited node if one exists.
        """
        next_node = None

        try:
            next_node = self.node_queue.popleft()

            while self.graph.nodes[next_node]["status"] is not None:
                next_node = self.node_queue.popleft()

        except:
            pass

        return next_node

    def generate_adjacencies(self):
        """
        Generate 4 adjacent positions to current robot position.
        """
        for delta in [
            Coord(-1, 0),
            Coord(1, 0),
            Coord(0, -1),
            Coord(0, 1),
        ]:
            yield self.pos + delta

    @staticmethod
    def get_directions():
        """
        Generate 4 directions of travel.
        """
        return deque(
            (
                Movement.north,
                Movement.south,
                Movement.west,
                Movement.east,
            )
        )

    def extract_target_coord(self):
        """
        Get the target coord from a fully build graph.
        """
        for node in self.graph.nodes:
            if self.graph.nodes[node]["status"] == Status.target:
                return node

    def board_str(self):
        """
        Produce a string representation of the board.
        """
        status_map = {
            Status.reachable: " ",
            Status.wall: "#",
            Status.target: "X",
            None: "?",
        }
        array = np.full((100, 100), " ")

        for node in self.graph:
            array[node.y, node.x] = status_map[self.graph.nodes[node]["status"]]

        array[self.pos.y, self.pos.x] = "D"
        return "\n".join("".join(row) for row in array)

    def get_solution_1(self):
        target = self.extract_target_coord()
        return nx.shortest_path_length(
            self.graph,
            self.start,
            target,
            weight="weight",
        )

    def get_solution_2(self):
        target = self.extract_target_coord()
        return max(
            list(
                nx.single_source_shortest_path_length(
                    self.graph,
                    target,
                ).values()
            )
        )


def parse(line):
    return list(map(int, line.strip().split(",")))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename):
    print(solve(parse(read_file(filename))))


if __name__ == "__main__":
    main("input.txt")
