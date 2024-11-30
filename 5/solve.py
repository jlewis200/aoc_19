#!/usr/bin/env python3

from collections import deque
from math import prod
from dataclasses import dataclass
from itertools import repeat, chain

POSITION_MODE = 0
IMMEDIATE_MODE = 1


@dataclass
class Args:

    ip: int
    next_ip: int
    instruction: int
    args: list[int] = None
    p_destination: int = None


def solve(program, input_queue, output_queue):
    ip = 0

    while program[ip] != 99:
        ip = process_instruction(program, ip, input_queue, output_queue)
        print(program_str(program))
        print(output_queue)
        print()

    assert output_queue.pop() == 5182797
    return program[0]


def program_str(program):
    string = "\t" + "\t".join("0123456789") + "\n"
    string += "-" * 90

    for idx, value in enumerate(program):

        if idx % 10 == 0:
            string += f"\n{idx}:\t{value}"
        else:
            string += f"\t{value}"

    return string


def process_instruction(program, ip, input_queue, output_queue):

    match get_opcode(program[ip]):

        case 1:
            args = get_args(program, ip, arg_types=("in", "in", "out"))
            program[args.p_destination] = sum(args.args)

        case 2:
            args = get_args(program, ip, arg_types=("in", "in", "out"))
            program[args.p_destination] = prod(args.args)

        case 3:
            args = get_args(program, ip, arg_types=("out",))
            program[args.p_destination] = input_queue.popleft()

        case 4:
            args = get_args(program, ip, arg_types=("in",))
            output_queue.append(args.args[0])

    print(args)
    return args.next_ip


def get_opcode(instruction):
    return instruction % 100


def get_parameter_modes(instruction):
    """
    Get the modes of an opcode's parameter.  Leading zeros are omitted from the
    opcode, so this generator will return 0s indefinitely.
    """
    modes = str(instruction // 100)
    modes = map(int, reversed(modes))
    yield from chain(modes, repeat(POSITION_MODE))


def get_arg(program, address, mode):
    if mode == 0:
        return program[program[address]]

    return program[address]


def get_args(program, ip, arg_types):
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
    instruction = program[ip]
    args = []
    p_destination = None
    parameter_modes = get_parameter_modes(program[ip])

    for arg_type in arg_types:
        ip += 1
        parameter_mode = next(parameter_modes)

        if arg_type == "in":
            args.append(get_arg(program, ip, parameter_mode))

        elif arg_type == "out":
            p_destination = get_arg(program, ip, IMMEDIATE_MODE)

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


def main(filename, input_queue, output_queue, expected=None):
    result = solve(
        parse(read_file(filename)),
        input_queue,
        output_queue,
    )
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    input_queue = deque([1])
    output_queue = deque()
    main("input.txt", input_queue, output_queue)
