"""Module allow to find the point of intersection two lines defined in points."""

import math


def object_intersection(line1, line2, width1, width2):
    """Find the point of intersecting lines.
       width1 - width of first unit
       width2 - width of second unit
    """
    line_1_array = [line1,
                    ((line1[0][0] - width1, line1[0][1] + width1), (line1[1][0] - width1, line1[1][1] - width1)),
                    ((line1[0][0] + width1, line1[0][1] + width1), (line1[1][0] + width1, line1[1][1] - width1)),
                    ((line1[0][0] + width1, line1[0][1] - width1), (line1[1][0] + width1, line1[1][1] + width1)),
                    ((line1[0][0] - width1, line1[0][1] - width1), (line1[1][0] + width1, line1[1][1] - width1))]
    line_2_array = [line2,
                    ((line2[0][0] - width2, line2[0][1] - width2), (line2[1][0] - width2, line2[1][1] - width2)),
                    ((line2[0][0] + width2, line2[0][1] + width2), (line2[1][0] + width2, line2[1][1] + width2)),
                    ((line2[0][0] + width2, line2[0][1] - width2), (line2[1][0] + width2, line2[1][1] + width2)),
                    ((line2[0][0] - width2, line2[0][1] - width2), (line2[1][0] + width2, line2[1][1] - width2))]
    for l1 in line_1_array:
        for l2 in line_2_array:
            xdiff = (l1[0][0] - l1[1][0], l2[0][0] - l2[1][0])
            ydiff = (l1[0][1] - l1[1][1], l2[0][1] - l2[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                continue

            d = (det(*l1), det(*l2))
            x = round(det(d, xdiff) / div)
            y = round(det(d, ydiff) / div)

            if point_in_area(l1, l2, x, y, width1, width2):
                return (x, y)
    return


def point_in_area(line1, line2, x, y, width1, width2):
    """Check if intersection point is on defined area."""
    x1, x2, x3, x4 = line1[0][0], line1[1][0], line2[0][0], line2[1][0]
    y1, y2, y3, y4 = line1[0][1], line1[1][1], line2[0][1], line2[1][1]
    return (min(x1, x2) <= x <= max(x1, x2) and min(x3, x4) <= x <= max(x3, x4) and
            min(y1, y2) <= y <= max(y1, y2) and min(y3, y4) <= y <= max(y3, y4))


def point_distance(p0, p1):
    return round(math.hypot(p0[0] - p1[0], p0[1] - p1[1]))


if __name__ == '__main__':
    A = (1, 1)
    B = (3, 2)
    C = (1, 3)
    D = (3, 1)
    int_point = object_intersection((A, B), (C, D), 2, 2)
    print(int_point)
    print(point_distance(A, int_point))
    print(point_distance(C, int_point))

    A = (1, 1)
    B = (0, 3)
    C = (1, 3)
    D = (0, 3)
    int_point = object_intersection((A, B), (C, D), 2, 2)
    print(int_point)
    print(point_distance(A, int_point))
    print(point_distance(C, int_point))

    A = (1, 3)
    B = (3, 3)
    C = (0, 3)
    D = (0, 2)
    int_point = object_intersection((A, B), (C, D), 2, 2)
    print(int_point)
