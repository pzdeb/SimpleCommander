import unittest
from src.simple_commander.controllers.main import GameController
from src.simple_commander.controllers.main import Hero


class MainControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.game_object = GameController(100, 100, 2)

    def test_game_field_width(self):
        self.assertEqual(self.game_object.game_field['width'], 100, 'incorrect game field width')

    def test_game_field_height(self):
        self.assertEqual(self.game_object.game_field['height'], 100, 'incorrect game field height')

    def test_game_field_units_length(self):
        self.assertEqual(len(self.game_object.units), 3, 'incorrect length of units')

    def test_bullet_create(self):
        self.game_object.fire(self.game_object.units[0])
        self.assertEqual(len(self.game_object.units), 4, 'Bullet was not created')

    def test_hero_start_speed(self):
        self.assertEqual(self.game_object.units[0].speed, 0, 'Incorrect initial speed')

    def test_hero_speed_after_change(self):
        self.game_object.units[0].change_speed(5)
        self.assertEqual(self.game_object.units[0].speed, 5, 'Incorrect initial speed')

    def test_hero_angle(self):
        hero = Hero(20, 20, 100)
        self.assertEqual(hero.angle, 100, 'Incorrect initial angle')

    def test_hero_angle_after_rotate(self):
        hero = Hero(20, 20, 100)
        hero.rotate(20)
        self.assertEqual(hero.angle, 120, 'Incorrect angle after rotate')

if __name__ == '__main__':
    unittest.main()