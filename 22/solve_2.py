#!/usr/bin/env python3

from collections import deque, defaultdict
import numpy as np
from sympy import *


def solve(actions, deck_size=10007, position=2020, iterations=1):
    """
    - all of the shuffle operations can be expressed as addition or multiplication mod deck_size
    - the same holds true for the inverse shuffle operations
    - a string expression is formed by applying the inverse shuffle operations in reverse order
    - this gives an expression representing a single application of the inverse shuffle
        f(x) = a*x + b

    - a and b are found by forming an expression using the shuffle steps and then simplifying with sympy
    - we are applying the function recursively for each iteration, ex. two inverse shuffles
        f(f(x))

    - for n applications of the inverse shuffle a geometric series is formed
        (a**n) * x + (b * (a**n - 1) // (a - 1)) mod deck_size

    - the division by (a-1) is replaced with the multiplicative inverse of (a-1) under deck size
    """
    expression = get_expression(actions, deck_size, position, iterations)
    expression = simplify(expression)

    x = symbols("x")
    a = expression.coeff(x)
    b = expression.coeff(x, 0)

    a %= deck_size
    b %= deck_size

    tmp_0 = pow(a, iterations, deck_size) * position
    tmp_1 = (pow(a, iterations, deck_size) - 1) * pow(a - 1, -1, deck_size)

    result = tmp_0 + (b * tmp_1)
    result %= deck_size
    return result


def get_expression(actions, deck_size=10007, position=2020, iterations=1):
    expression = "x"

    for function, arg in actions:
        expression = function(deck_size, arg, expression)

    return expression


def inverse_increment(deck_size, interval, expression):
    multiplicative_inverse = pow(interval, -1, deck_size)
    return f"({expression}) * {multiplicative_inverse}"


def inverse_cut(deck_size, cut_position, expression):
    return f"({expression}) + {cut_position}"


def inverse_stack(deck_size, _, expression):
    return f"-({expression}) - 1"


def parse(lines):
    parsed = []

    for line in lines:
        line = line.strip()

        if "stack" in line:
            parsed.append((inverse_stack, None))

        elif "increment" in line:
            parsed.append((inverse_increment, int(line.split()[-1])))

        elif "cut" in line:
            parsed.append((inverse_cut, int(line.split()[-1])))

    return parsed[::-1]


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename):
    assert (
        solve(parse(read_file(filename)), deck_size=10007, position=1510, iterations=1)
        == 2019
    )
    assert (
        solve(parse(read_file(filename)), deck_size=10007, position=9488, iterations=2)
        == 2019
    )
    assert (
        solve(parse(read_file(filename)), deck_size=10007, position=4113, iterations=3)
        == 2019
    )
    print(
        solve(
            parse(read_file(filename)),
            deck_size=119315717514047,
            position=2020,
            iterations=101741582076661,
        )
    )


if __name__ == "__main__":
    main("input.txt")
