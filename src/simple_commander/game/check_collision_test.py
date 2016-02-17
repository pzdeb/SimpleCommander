import asyncio
import datetime
import math
import time
import unittest

from SimpleCommander.src.simple_commander.game.hero import Hero
from SimpleCommander.src.simple_commander.game.invader import Invader


class Controller():
    game_field = {'height': 1000, 'width': 1000}
    collisions = {}

    @asyncio.coroutine
    def notify_clients(self, data):
        pass

    def check_collision(self, unit, interval):
        pass


class MainControllerTestCase(unittest.TestCase):
    def setUp(self):
        controller = Controller()
        self.unit1 = Hero(0, 0, 45, 0, 0, 1, 0.5, 'hero', 'bullet_hero', 10, controller)
        self.unit2 = Invader(10, 10, 45, 0, 10, 'invader1', 'bullet_invader', 10, controller)
        controller.collisions[self.unit1.id] = []
        controller.collisions[self.unit2.id] = []

    def tearDown(self):
        del self.unit1
        del self.unit2

    def test_compute_new_coordinate(self):
        unit = Invader(500, 500, 0, 10, 100, 'invader1', 'bullet_invader', 10, Controller())
        while unit.angle < 360:
            unit.compute_new_coordinate(1)
            distance = math.sqrt(((unit.x1-unit.x)**2)+((unit.y1-unit.y)**2))
            self.assertTrue(0.01 <= distance/unit.speed <= 1.01)
            unit.angle += 20

    def test_collision(self):
        self.unit1.x, self.unit1.x1 = 500, 500
        self.unit1.y, self.unit1.y1 = 500, 500
        self.unit1.speed = 10
        self.unit1.angle = 90
        self.unit2.x, self.unit2.x1 = 600, 600
        self.unit2.y, self.unit2.y1 = 500, 500
        self.unit2.speed = 10
        self.unit2.angle = 270
        self.assertFalse(self.unit1.is_dead and self.unit2.is_dead)
        for i in range(0, 5):
            self.unit1.last_calculation_time -= datetime.timedelta(seconds=10)
            self.unit2.last_calculation_time -= datetime.timedelta(seconds=10)
            self.unit1.compute_new_coordinate(1)
            self.unit2.compute_new_coordinate(1)
            self.unit1.check_collision(self.unit2, 1)
            print(self.unit1.x1, self.unit1.y1, self.unit1.angle, self.unit2.x1, self.unit2.y1, self.unit2.angle, i)
            if i < 4:
                self.assertFalse(self.unit1.is_dead and self.unit2.is_dead)
            else:
                time.sleep(1)
                print(self.unit1.life_count, self.unit1.is_dead, self.unit2.is_dead)
                self.assertTrue(self.unit1.is_dead and self.unit2.is_dead)


if __name__ == '__main__':
    unittest.main()