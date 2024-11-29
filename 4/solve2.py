#!/usr/bin/env python3

from numpy.lib.stride_tricks import sliding_window_view
from numpy import unique


def solve(range_start, range_end):
    valid_count = 0

    for number in range(range_start, range_end + 1):
        valid_count += valid(number)

    return valid_count


def valid(number):
    return valid_adjacent(number) and valid_non_decreasing(number)


def valid_non_decreasing(number):
    decreasing_count = 0
    number = split_number(number)

    for digit_0, digit_1 in sliding_window_view(number, 2):
        decreasing_count += digit_0 > digit_1

    return decreasing_count == 0


def valid_adjacent(number):
    """
    Because the digits and non-decreasing, every occurrence of a number will
    be adjacent.  Checking for a value count of 2 suffices.
    """
    adjacent_count = 0
    number = split_number(number)
    _, counts = unique(number, return_counts=True)
    return 2 in counts


def split_number(number):
    digits = list(f"{number}")
    return list(map(int, digits))


if __name__ == "__main__":
    assert valid(112233)
    assert not valid(123444)
    assert valid(111122)
    print(solve(178416, 676461))
