import unittest

from simple_commander.utils.line_intersection import object_intersection


class MainControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.unit1 = {'width': 2}
        self.unit2 = {'width': 2}

    def tearDown(self):
        del self.unit1
        del self.unit2

    def test_intersection_1(self):
        A = (1, 1)
        B = (4, 2)
        C = (1, 4)
        D = (4, 1)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, (2.25, 2.0, 4.25, 2.75) )

    def test_intersection_2(self):
        A = (1, 7)
        B = (5, 2)
        C = (11, 7)
        D = (6, 2)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        #self.assertEqual(int_point, (6, 2), 'incorrect point for intersection')
        self.assertEqual(int_point.bounds, (5.0, 3.0, 6.0, 3.333333333333333) )

    def test_intersection_3(self):
        A = (5, 2)
        B = (1, 7)
        C = (11, 7)
        D = (6, 2)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, ())

    def test_intersection_4(self):
        A = (1, 7)
        B = (5, 2)
        C = (6, 2)
        D = (11, 7)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, ())

    def test_intersection_5(self):
        A = (5, 2)
        B = (1, 7)
        C = (6, 2)
        D = (11, 7)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, (5.0, 1.0, 6.0, 1.7777777777777777))

    def test_intersection_6(self):
        A = (5, 2)
        B = (1, 7)
        C = (8, 2)
        D = (11, 7)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, ())

    def test_intersection_7(self):
        A = (4, 4)
        B = (4, 4)
        C = (1, 1)
        D = (7, 7)
        int_point = object_intersection(A, B,C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, (3.0, 3.0, 5.0, 5.0))

    def test_intersection_8(self):
        A = (1, 1)
        B = (1, 10)
        C = (2, 2)
        D = (2, 10)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, (1.0, 1.0, 2.0, 11.0))

    def test_intersection_9(self):
        A = (1, 1)
        B = (1, 10)
        C = (4, 4)
        D = (4, 10)
        int_point = object_intersection(A, B, C, D, round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point.bounds, ())

if __name__ == '__main__':
    unittest.main()