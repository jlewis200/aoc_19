#!/usr/bin/env python3

from collections import deque, defaultdict
from math import prod
from dataclasses import dataclass
from itertools import repeat, chain, permutations
import numpy as np


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

    def gcd_reduce(self):
        """
        Reduce the y/x coord by the greatest common divisor.  Ex:

         2,  2 ->  1,  1
        -3, -9 -> -1, -3
        """
        if self.y == 0 or self.x == 0:
            divisor = max(abs(self.y), abs(self.x), 1)
        else:
            divisor = gcd(self.y, self.x)

        return Coord(self.y // divisor, self.x // divisor)

    @classmethod
    def set_ranges(cls, asteroids):
        y_max = max(asteroid.y for asteroid in asteroids)
        x_max = max(asteroid.x for asteroid in asteroids)
        cls.y_range = range(y_max + 1)
        cls.x_range = range(x_max + 1)

    def valid(self):
        return self.y in self.y_range and self.x in self.x_range


def solve(program):
    interpreter = Interpreter(program)
    pixels = defaultdict(lambda: 0)
    output_queue = interpreter.run(deque())

    while len(output_queue) > 0:
        x = output_queue.popleft()
        y = output_queue.popleft()
        tile_id = output_queue.popleft()
        pixels[(x, y)] = tile_id

    return list(pixels.values()).count(2)


def parse(line):
    return list(map(int, line.strip().split(",")))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename):
    print(solve(parse(read_file(filename))))


if __name__ == "__main__":
    main("input.txt")
