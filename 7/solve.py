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


@dataclass
class Args:
    instruction: int
    args: list[int] = None
    p_destination: int = None


def solve(program):
    max_signal = 0

    for phase_sequence in permutations([0, 1, 2, 3, 4]):
        signal = 0

        for phase in phase_sequence:
            interpreter = Interpreter(program)
            signal = get_signal(interpreter, phase, signal)

        max_signal = max(max_signal, signal)

    return max_signal


def get_signal(program, phase, input_signal):
    input_queue = deque([phase, input_signal])
    output_queue = program.run(input_queue)
    return output_queue.pop()


class Interpreter:

    def __init__(self, program):
        self.ip = 0
        self.program = program
        self.input_queue = deque()
        self.output_queue = deque()
        self.terminated = False

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
        self.input_queue.extend(input_queue)

        while not self.terminated:
            self.process_instruction()

        return self.output_queue

    def add(self):
        args = self.get_args(arg_types=("in", "in", "out"))
        self.program[args.p_destination] = sum(args.args)

    def mult(self):
        args = self.get_args(arg_types=("in", "in", "out"))
        self.program[args.p_destination] = prod(args.args)

    def input(self):
        try:
            input_value = self.input_queue.popleft()
        except IndexError:
            return None
        args = self.get_args(arg_types=("out",))
        self.program[args.p_destination] = input_value

    def output(self):
        args = self.get_args(arg_types=("in",))
        self.output_queue.append(args.args[0])

    def jump_not_zero(self):
        args = self.get_args(arg_types=("in", "in"))
        if args.args[0] != 0:
            self.ip = args.args[1]

    def jump_zero(self):
        args = self.get_args(arg_types=("in", "in"))
        if args.args[0] == 0:
            self.ip = args.args[1]

    def less_than(self):
        args = self.get_args(arg_types=("in", "in", "out"))
        if args.args[0] < args.args[1]:
            self.program[args.p_destination] = 1
        else:
            self.program[args.p_destination] = 0

    def equal(self):
        args = self.get_args(arg_types=("in", "in", "out"))
        if args.args[0] == args.args[1]:
            self.program[args.p_destination] = 1
        else:
            self.program[args.p_destination] = 0

    def terminate(self):
        self.terminated = True
        return None

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
                p_destination = self.get_arg(self.ip, IMMEDIATE_MODE)

        self.ip += 1

        return Args(
            instruction=instruction,
            p_destination=p_destination,
            args=args,
        )


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
    main("test_0.txt", 43210)
    main("test_1.txt", 54321)
    main("test_2.txt", 65210)
    main("input.txt", 206580)
