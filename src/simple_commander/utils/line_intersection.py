"""Module allow to find the point of intersection two  Polygon defined in points."""

from shapely.geometry import Polygon

def object_intersection(A, B, C, D, width1, width2):
    """Find the area of Polygons intersecting .
       width1 - width of first unit
       width2 - width of second unit
    """

    first_unit_path = Polygon([(A[0] - width1, A[1] - width1), (B[0] - width1, B[1] + width1),
                               (B[0] + width1, B[1] + width1), (A[0] + width1, A[1] - width1)])

    second_unit_path = Polygon([(C[0] - width2, C[1] - width2), (D[0] - width2, D[1] + width2),
                                (D[0] + width2, D[1] + width2), (C[0] + width2, C[1] - width2)])

    intersection_area = first_unit_path.intersection(second_unit_path)
    return intersection_area


if __name__ == '__main__':
    A = (381, 397)
    B = (437, 322)
    C = (440, 338)
    D = (483, 378)
    int_point = object_intersection(A, B, C, D, 14, 14)
    print(int_point)

