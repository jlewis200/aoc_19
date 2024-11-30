#!/usr/bin/env python3

from itertools import product
import numpy as np


def solve(image):
    rendered_image = np.zeros(shape=(image.shape[1:]), dtype=str)

    for y, x in product(range(image.shape[1]), range(image.shape[2])):
        depth_slice = image[:, y, x]
        depth_slice = depth_slice[depth_slice != 2]
        rendered_image[y, x] = "#" if depth_slice[0] == 1 else " "

    print(image_str(rendered_image))


def image_str(image):
    image_string = ""

    for row in image:
        for element in row:
            image_string += element
        image_string += "\n"
    return image_string


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
    main("test2.txt", 2, 2)
    main("input.txt", 25, 6)
