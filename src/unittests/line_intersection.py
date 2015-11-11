import unittest

from src.simple_commander.utils.line_intersection import object_intersection


class MainControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.unit1 = {'width': 2}
        self.unit2 = {'width': 2}

    def tearDown(self):
        del self.unit1
        del self.unit2

    def test_intersection_1(self):
        A = (1, 1)
        B = (3, 2)
        C = (1, 3)
        D = (3, 1)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (2, 2), 'incorrect point for intersection')

    def test_intersection_2(self):
        A = (1, 7)
        B = (5, 2)
        C = (11, 7)
        D = (6, 2)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (6, 2), 'incorrect point for intersection')

    def test_intersection_3(self):
        A = (5, 2)
        B = (1, 7)
        C = (11, 7)
        D = (6, 2)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (6, 2), 'incorrect point for intersection')

    def test_intersection_4(self):
        A = (1, 7)
        B = (5, 2)
        C = (6, 2)
        D = (11, 7)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (6, 2), 'incorrect point for intersection')

    def test_intersection_5(self):
        A = (5, 2)
        B = (1, 7)
        C = (6, 2)
        D = (11, 7)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (6, 2), 'incorrect point for intersection')

    def test_intersection_6(self):
        A = (5, 2)
        B = (1, 7)
        C = (8, 2)
        D = (11, 7)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, None, 'incorrect point for intersection')

    def test_intersection_7(self):
        A = (4, 4)
        B = (4, 4)
        C = (1, 1)
        D = (7, 7)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (3, 3), 'incorrect point for intersection')

    def test_intersection_8(self):
        A = (1, 1)
        B = (1, 10)
        C = (2, 2)
        D = (2, 10)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, (1, 1), 'incorrect point for intersection')

    def test_intersection_9(self):
        A = (1, 1)
        B = (1, 10)
        C = (4, 4)
        D = (4, 10)
        int_point = object_intersection((A, B), (C, D), round(self.unit1['width'] / 2), round(self.unit2['width'] / 2))
        self.assertEqual(int_point, None, 'incorrect point for intersection')

if __name__ == '__main__':
    unittest.main()