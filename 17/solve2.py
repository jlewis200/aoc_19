#!/usr/bin/env python3

from collections import deque, defaultdict
from itertools import repeat, chain
import numpy as np
from pprint import pprint


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

    @property
    def c(self):
        return (self.y, self.x)


deltas = {
    0: Coord(-1, 0),  # up
    1: Coord(0, 1),  # right
    2: Coord(1, 0),  # down
    3: Coord(0, -1),  # left
}


def solve(program):
    """
    [('L', 10),   A
     ('R', 12),
     ('R', 12),

     ('R', 6),    B
     ('R', 10),
     ('L', 10),

     ('L', 10),   A
     ('R', 12),
     ('R', 12),

     ('R', 10),   C
     ('L', 10),
     ('L', 12),
     ('R', 6),

     ('R', 6),    B
     ('R', 10),
     ('L', 10),

     ('R', 10),   C
     ('L', 10),
     ('L', 12),
     ('R', 6),

     ('R', 6),    B
     ('R', 10),
     ('L', 10),

     ('R', 10),   C
     ('L', 10),
     ('L', 12),
     ('R', 6),

     ('L', 10),   A
     ('R', 12),
     ('R', 12),

     ('R', 10),   C
     ('L', 10),
     ('L', 12),
     ('R', 6)]

     movement program:
     "A,B,A,C,B,C,B,C,A,C"

     movement functions:
     A: "L,10,R,12,R,12"
     B: "R,6,R,10,L,10"
     C: "R,10,L,10,L,12,R,6"
    """
    interpreter = Interpreter(program)
    board = np.array(get_board(interpreter.run(deque())))
    vacuum = Coord(*np.argwhere(board == "^")[0])
    orientation = 0

    orientations = [orientation]
    distances = []

    while get_orientation(board, vacuum, orientation) is not None:
        orientation = get_orientation(board, vacuum, orientation)
        segment_length = get_segment_length(board, vacuum, orientation)
        vacuum += deltas[orientation] * segment_length
        orientations.append(orientation)
        distances.append(segment_length)

    turns = [
        get_turn(pair)
        for pair in np.lib.stride_tricks.sliding_window_view(orientations, 2)
    ]
    pprint(list(zip(turns, distances)))

    # solution derived manually
    movement_program = "A,B,A,C,B,C,B,C,A,C\n"
    f_a = "L,10,R,12,R,12\n"
    f_b = "R,6,R,10,L,10\n"
    f_c = "R,10,L,10,L,12,R,6\n"
    interactive = "n\n"

    input_queue = deque()

    for char in movement_program + f_a + f_b + f_c + interactive:
        input_queue.append(ord(char))

    interpreter = Interpreter(program)
    output = interpreter.run(input_queue)
    print(output[-1])


def get_turn(directions):
    start, end = directions

    return {
        (0, 1): "R",
        (0, 3): "L",
        (1, 2): "R",
        (1, 0): "L",
        (2, 3): "R",
        (2, 1): "L",
        (3, 0): "R",
        (3, 2): "L",
    }[(start, end)]


def get_segment_length(board, vacuum, orientation):
    segment_length = 0

    while (
        (vacuum + deltas[orientation]).c[0] in range(board.shape[0])
        and (vacuum + deltas[orientation]).c[1] in range(board.shape[1])
        and board[(vacuum + deltas[orientation]).c] == "#"
    ):
        segment_length += 1
        vacuum += deltas[orientation]

    return segment_length


def get_orientation(board, vacuum, orientation):
    for offset in (1, -1):
        new_orientation = (orientation + offset) % 4

        if (
            (vacuum + deltas[new_orientation]).c[0] in range(board.shape[0])
            and (vacuum + deltas[new_orientation]).c[1] in range(board.shape[1])
            and board[(vacuum + deltas[new_orientation]).c] == "#"
        ):
            return new_orientation


def get_board(output_queue):
    board = "".join(map(chr, output_queue)).split()
    print("\n".join(board))
    board = [list(row) for row in board]
    board = board[:-1]
    return np.array(board)


def get_intersections(board):
    intersections = set()
    mask = np.array(
        [
            [".", "#", "."],
            ["#", "#", "#"],
            [".", "#", "."],
        ]
    )

    for y in range(board.shape[0] - mask.shape[0]):
        for x in range(board.shape[1] - mask.shape[1]):
            board_slice = board[y : y + mask.shape[0], x : x + mask.shape[1]]

            if (board_slice == mask).all():
                intersections.add((y + 1, x + 1))

    return intersections


def parse(line):
    return list(map(int, line.strip().split(",")))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename):
    print(solve(parse(read_file(filename))))


if __name__ == "__main__":
    main("input2.txt")
