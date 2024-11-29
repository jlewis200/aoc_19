#!/usr/bin/env python3


from re import match


class Wire:
    """
    This class records the occupied coordinates it travels through and the step
    count to reach the coordinate.  If visited multiple times, only the first is
    recorded.
    """

    def __init__(self, path):
        self.x = 0
        self.y = 0
        self.step = 0
        self.step_count = {}
        self.coords = set()
        self.travel_path(path)

    def travel_path(self, path):
        for direction, distance in path:
            self.travel_path_segment(*self.get_delta(direction), distance)

    def travel_path_segment(self, dx, dy, distance):
        for _ in range(distance):
            self.step += 1
            self.x += dx
            self.y += dy
            coord = (self.x, self.y)
            self.coords.add(coord)

            if coord not in self.step_count:
                self.step_count[coord] = self.step

    @staticmethod
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


def solve(path_0, path_1):
    wire_0 = Wire(path_0)
    wire_1 = Wire(path_1)
    intersections = wire_0.coords & wire_1.coords
    return find_soonest(intersections, wire_0.step_count, wire_1.step_count)


def find_soonest(coords, step_count_0, step_count_1):
    min_steps = 2**32

    for coord in coords:
        min_steps = min(min_steps, step_count_0[coord] + step_count_1[coord])

    return min_steps


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
    main("test_0.txt", 30)
    main("test_1.txt", 610)
    main("test_2.txt", 410)
    main("input.txt")
