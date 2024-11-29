#!/usr/bin/env python3

from numpy.lib.stride_tricks import sliding_window_view


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
    adjacent_count = 0
    number = split_number(number)

    for digit_0, digit_1 in sliding_window_view(number, 2):
        adjacent_count += digit_0 == digit_1

    return adjacent_count > 0


def split_number(number):
    digits = list(f"{number}")
    return list(map(int, digits))


if __name__ == "__main__":
    assert valid(111111)
    assert not valid(223450)
    assert not valid(123789)
    print(solve(178416, 676461))
