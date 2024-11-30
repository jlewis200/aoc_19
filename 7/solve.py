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

    ip: int
    next_ip: int
    instruction: int
    args: list[int] = None
    p_destination: int = None


def solve(program):
    program = Program(program)
    max_signal = 0

    for phase_sequence in permutations([0, 1, 2, 3, 4]):
        signal = 0

        for phase in phase_sequence:
            signal = get_signal(program, phase, signal)

        max_signal = max(max_signal, signal)

    return max_signal


def get_signal(program, phase, input_signal):
    input_queue = deque([phase, input_signal])
    output_queue = program.run(input_queue)
    return output_queue.pop()


class Program:

    def __init__(self, program):
        self.program = None
        self.original_program = program
        self.input_queue = None
        self.output_queue = deque()

    def __str__(self):
        string = "\t" + "\t".join("0123456789") + "\n"
        string += "-" * 90

        for idx, value in enumerate(self.program):

            if idx % 10 == 0:
                string += f"\n{idx}:\t{value}"
            else:
                string += f"\t{value}"

        return string

    def run(self, input_queue):
        ip = 0
        self.program = self.original_program.copy()
        self.input_queue = input_queue

        while self.program[ip] != Opcode.TERMINATE:
            ip = self.process_instruction(ip)

        return self.output_queue

    def process_instruction(self, ip):
        match self.get_opcode(self.program[ip]):

            case Opcode.ADD:
                args = self.get_args(ip, arg_types=("in", "in", "out"))
                self.program[args.p_destination] = sum(args.args)

            case Opcode.MULT:
                args = self.get_args(ip, arg_types=("in", "in", "out"))
                self.program[args.p_destination] = prod(args.args)

            case Opcode.INPUT:
                args = self.get_args(ip, arg_types=("out",))
                self.program[args.p_destination] = self.input_queue.popleft()

            case Opcode.OUTPUT:
                args = self.get_args(ip, arg_types=("in",))
                self.output_queue.append(args.args[0])

            case Opcode.JUMP_NOT_ZERO:
                args = self.get_args(ip, arg_types=("in", "in"))
                if args.args[0] != 0:
                    args.next_ip = args.args[1]

            case Opcode.JUMP_ZERO:
                args = self.get_args(ip, arg_types=("in", "in"))
                if args.args[0] == 0:
                    args.next_ip = args.args[1]

            case Opcode.LESS_THAN:
                args = self.get_args(ip, arg_types=("in", "in", "out"))
                if args.args[0] < args.args[1]:
                    self.program[args.p_destination] = 1
                else:
                    self.program[args.p_destination] = 0

            case Opcode.EQUAL:
                args = self.get_args(ip, arg_types=("in", "in", "out"))
                if args.args[0] == args.args[1]:
                    self.program[args.p_destination] = 1
                else:
                    self.program[args.p_destination] = 0

        return args.next_ip

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

    def get_args(self, ip, arg_types):
        """
        Arg types:
            in: possibly dereferenced
            out: never dereferenced

        In parameters are dereferenced if parameter mode is 0 (positions mode),
        and the raw value is returned for mode 1 (immediate mode).

        Out parameters are not dereferenced.
        """
        assert isinstance(arg_types, (tuple, list))

        old_ip = ip
        instruction = self.program[ip]
        args = []
        p_destination = None
        parameter_modes = self.get_parameter_modes(self.program[ip])

        for arg_type in arg_types:
            ip += 1
            parameter_mode = next(parameter_modes)

            if arg_type == "in":
                args.append(self.get_arg(ip, parameter_mode))

            elif arg_type == "out":
                p_destination = self.get_arg(ip, IMMEDIATE_MODE)

        return Args(
            ip=old_ip,
            next_ip=ip + 1,
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
    result = solve(
        parse(read_file(filename)),
    )
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test_0.txt", 43210)
    main("test_1.txt", 54321)
    main("test_2.txt", 65210)
    main("input.txt")
