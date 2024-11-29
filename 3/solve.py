#!/usr/bin/env python3


from re import match


def solve(path_0, path_1):
    coords_0 = get_coords(path_0)
    coords_1 = get_coords(path_1)

    intersections = coords_0 & coords_1
    return find_closest(intersections)


def find_closest(coords):
    distances = {get_distance(*coord) for coord in coords}
    return min(distances)


def get_distance(x, y):
    return abs(x) + abs(y)


def get_coords(path):
    coords = set()
    x, y = 0, 0

    for direction, distance in path:
        coords_, x, y = get_segment_coords(x, y, *get_delta(direction), distance)
        coords |= coords_

    return coords


def get_segment_coords(x, y, dx, dy, distance):
    coords = set()

    for _ in range(distance):
        x += dx
        y += dy
        coords.add((x, y))

    return coords, x, y


def get_delta(direction):
    dx, dy = 0, 0

    match direction:

        case "L":
            return -1, 0

        case "R":
            return 1, 0

        case "U":
            return 0, -1

        case "D":
            return 0, 1


def parse(lines):
    return map(parse_path, lines)


def parse_path(segments):
    path = []

    for segment in segments.split(","):
        match_ = match("(?P<direction>[RLDU])(?P<distance>\d+)", segment)
        path.append(
            (
                match_.group("direction"),
                int(match_.group("distance")),
            )
        )

    return path


def read_file(filename):
    with open(filename, encoding="utf-8") as f_in:
        return f_in.readlines()


def main(filename, expected=None):
    result = solve(*parse(read_file(filename)))
    print(result)
    if expected is not None:
        assert result == expected


if __name__ == "__main__":
    main("test_0.txt", 6)
    main("test_1.txt", 159)
    main("test_2.txt", 135)
    main("input.txt")
