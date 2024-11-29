#!/usr/bin/env python3

from itertools import product


def solve(program, target):
    for noun, verb in product(list(range(100)), repeat=2):
        if run(program.copy(), noun, verb) == target:
            return int(f"{noun}{verb}")


def run(program, noun, verb):
    ip = 0
    program[1] = noun
    program[2] = verb

    while program[ip] != 99:
        ip = process_instruction(program, ip)

    return program[0]


def process_instruction(program, ip):
    p_arg_0 = program[ip + 1]
    p_arg_1 = program[ip + 2]
    p_destination = program[ip + 3]

    arg_0 = program[p_arg_0]
    arg_1 = program[p_arg_1]

    match program[ip]:

        case 1:
            result = arg_0 + arg_1

        case 2:
            result = arg_0 * arg_1

    program[p_destination] = result
    return ip + 4


def parse(line):
    return list(map(int, line.strip().split(",")))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename, target, expected=None):
    result = solve(
        parse(read_file(filename)),
        target,
    )
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("input.txt", 19690720)
