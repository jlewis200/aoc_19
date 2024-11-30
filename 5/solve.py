#!/usr/bin/env python3

from collections import deque
from math import prod
from dataclasses import dataclass


@dataclass
class Args:

    next_ip: int
    p_destination: int
    args: list[int] = None


def solve(program, input_queue, output_queue):
    ip = 0

    print(program)
    print(ip)
    print()
    breakpoint()

    while program[ip] != 99:
        ip = process_instruction(program, ip, input_queue, output_queue)
        print(program)
        print(ip)
        print()
        breakpoint()
    return program[0]


def process_instruction(program, ip, input_queue, output_queue):
    match program[ip]:

        case 1:
            args = get_args(program, ip, arg_count=3)
            program[args.p_destination] = sum(args.args)

        case 2:
            args = get_args(program, ip, arg_count=3)
            program[args.p_destination] = prod(args.args)

        case 3:
            args = get_args(program, ip, arg_count=1)
            program[args.p_destination] = input_queue.popleft()

        case 4:
            args = get_args(program, ip, arg_count=1)
            output_queue.append(program[args.p_destination])
    
    print(args)
    return args.next_ip


def get_parameter_modes(instruction):
    modes = list(str(instruction // 100))

    for mode in modes:
        yield int(mode)

    while True:
        yield 0


def get_arg(program, address, mode):
    if mode == 0:
        return program[program[address]]

    return program[address]


def get_args(program, ip, arg_count):

    args = []
    parameter_modes = get_parameter_modes(program[ip])

    while len(args) < arg_count:
        ip += 1
        parameter_mode = next(parameter_modes)
        args.append(get_arg(program, ip, parameter_mode))

    return Args(
        next_ip=ip + 1,
        p_destination=args.pop(),
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
