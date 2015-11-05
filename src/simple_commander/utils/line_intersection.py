"""Module allow to find the point of intersection two lines defined in points."""

import math


def line_intersection(line1, line2):
    """Find the point of intersecting lines."""
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return

    d = (det(*line1), det(*line2))
    x = round(det(d, xdiff) / div)
    y = round(det(d, ydiff) / div)

    if point_in_area(line1, line2, x, y):
        return (x, y)


def point_in_area(line1, line2, x, y):
    """Check if intersection point is on defined area."""
    x1, x2, x3, x4 = line1[0][0], line1[1][0], line2[0][0], line2[1][0]
    y1, y2, y3, y4 = line1[0][1], line1[1][1], line2[0][1], line2[1][1]
    return (x1 <= x and x2 >= x and x3 <= x and x4 >= x)\
           or (y1 <= y and y2 >= y and y3 <= y  and y4 >= y)


def point_distance(x, y):
    return round(math.hypot(x[1] - x[0], y[1] - y[0]))


if __name__ == '__main__':
    A = (1, 1)
    B = (3, 2)
    C = (1, 3)
    D = (3, 1)
    int_point = line_intersection((A, B), (C, D))
    print(int_point)
    print(point_distance(A, int_point))
    print(point_distance(C, int_point))

    A = (1, 1)
    B = (0, 3)
    C = (1, 3)
    D = (0, 3)
    int_point = line_intersection((A, B), (C, D))
    print(int_point)
    print(point_distance(A, int_point))
    print(point_distance(C, int_point))

    A = (1, 3)
    B = (3, 3)
    C = (0, 3)
    D = (0, 2)
    int_point = line_intersection((A, B), (C, D))
    print(int_point)
