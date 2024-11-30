#!/usr/bin/env python3

from collections import deque
from math import prod
from dataclasses import dataclass
from itertools import repeat, chain, permutations

POSITION_MODE = 0
IMMEDIATE_MODE = 1


class Opcode:
    ADD = 1
    MULT = 2
    INPUT = 3
    OUTPUT = 4
    JUMP_NOT_ZERO = 5
    JUMP_ZERO = 6
    LESS_THAN = 7
    EQUAL = 8
    TERMINATE = 99


class Interpreter:

    def __init__(self, program):
        self.ip = 0
        self.program = program.copy()
        self.input_queue = deque()
        self.output_queue = deque()
        self.state = "initialized"

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
        yield from chain(modes, repeat(POSITION_MODE))

    def get_arg(self, address, mode):
        if mode == 0:
            return self.program[self.program[address]]

        return self.program[address]

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
                args.append(self.get_arg(self.ip, parameter_mode))

            elif arg_type == "out":
                args.append(self.get_arg(self.ip, IMMEDIATE_MODE))

        self.ip += 1

        if len(args) == 1:
            return args.pop()

        return args


def solve(program):
    max_signal = 0

    for phase_sequence in permutations([5, 6, 7, 8, 9]):
        signal = evaluate_phase_sequence(program, phase_sequence)
        max_signal = max(max_signal, signal)

    return max_signal


def evaluate_phase_sequence(program, phase_sequence):
    signal = 0
    interpreters = initialize_interpreters(program, phase_sequence)

    while any(interpreter.state != "terminated" for interpreter in interpreters):
        signal = perform_round(interpreters, signal)

    return signal


def perform_round(interpreters, signal):
    for interpreter in interpreters:
        signal = get_signal(interpreter, signal)

    return signal


def get_signal(interpreter, signal):
    output_queue = interpreter.run(deque([signal]))
    return output_queue.pop()


def initialize_interpreters(program, phase_sequence):
    interpreters = []

    for phase in phase_sequence:
        interpreter = Interpreter(program)
        interpreter.run(deque([phase]))
        interpreters.append(interpreter)

    return interpreters


def parse(line):
    return list(map(int, line.strip().split(",")))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename, expected=None):
    result = solve(parse(read_file(filename)))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test_3.txt", 139629729)
    main("test_4.txt", 18216)
    main("input.txt")
