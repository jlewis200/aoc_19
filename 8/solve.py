#!/usr/bin/env python3

import numpy as np


def solve(image):
    min_zeros = 2**32
    min_layer = None

    for layer in image:
        zero_count = (layer == 0).sum()

        if zero_count < min_zeros:
            min_layer = layer
            min_zeros = zero_count

    one_count = (min_layer == 1).sum()
    two_count = (min_layer == 2).sum()
    return one_count * two_count


def parse(data, width, height):
    """
    Return image as numpy array of shape (n-layers, height, width).
    """
    digits = list(data.strip())
    digits = list(map(int, digits))
    image = np.array(digits)
    return image.reshape((-1, height, width))


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.read()


def main(filename, width, height, expected=None):
    result = solve(parse(read_file(filename), width, height))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    """
    too high:
    2208
    """
    main("test.txt", 3, 2, 1)
    main("input.txt", 25, 6)
