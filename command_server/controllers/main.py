#!/usr/bin/env python3
import asyncio
import json
import logging
from random import randint
import math

'''
In this game we have two role - invader and hero. Both can bullet.

Invaders are located at the top of game field and always move from the right side to the left and revert.
Also they slowly move to the bottom.

Main hero is located at the centre at the bottom. He can move to the left and to the right.
If he bullet some invader, his bonus is grow.
When invader bullet to main hero, the main hero's life is decrease.
'''

IMAGE_FILENAME = {'background': 'images/bg.png',
                  'hero': 'images/hero.png',
                  'bullet_hero': 'images/bullet_hero',
                  'bullet_invader': 'images/bullet_invader',
                  'invader': ['images/invader1.png', 'images/invader2.png']
                  }

DEFAULT_SPEED = 5
TIME_TO_SLEEP = 1

g = 9.81

GAME_OBJ = None


def get_game_controller():
    global GAME_OBJ
    if not GAME_OBJ:
        GAME_OBJ = GameController(50, 50, 2)
    return GAME_OBJ


class Unit(object):

    def __init__(self, x, y, angle, bonus, speed, unit_filename, bullet_filename):
        self.image_filename = unit_filename
        self.bullet_filename = bullet_filename
        self.x = x
        self.y = y
        self.x0 = x
        self.y0 = y
        self.angle = angle
        self.width = 10  # temporary when we don't have real images
        self.height = 10  # must be height of real image
        self.bonus = bonus
        self.speed = speed
        self.is_dead = False

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def rotate(self, angle):
        self.angle += angle

    def change_speed(self, speed):
        new_speed = self.speed + speed
        self.speed = new_speed or 0

    def check_collision(self, other_unit):
        # check if coordinate for two units is the same
        # for this check we also include width and height of unit's image
        # (other_unit.x - other_unit.width / 2 < self.x < other_unit.x + other_unit.width / 2)
        # (other_unit.y - other_unit.height / 2 < self.y < other_unit.y + other_unit.height / 2)
        if (self.x > other_unit.x - other_unit.width / 2) and (self.x < other_unit.x + other_unit.width / 2) and \
                (self.y > other_unit.y - other_unit.height / 2) and (self.y < other_unit.y + other_unit.height / 2):
            self.kill(other_unit)

    def kill(self, other_unit):
        raise NotImplementedError


class Invader(Unit):

    def __init__(self, x, y, angle, bonus=10, speed=DEFAULT_SPEED, unit_filename='',
                 bullet_filename=IMAGE_FILENAME.get('bullet_invader', '')):
        if not unit_filename and len(IMAGE_FILENAME.get('invader', [])):
            random_number = randint(0, len(IMAGE_FILENAME.get('invader', [])) - 1)
            unit_filename = IMAGE_FILENAME.get('invader', [])[random_number]
        super(Invader, self).__init__(x, y, angle, bonus, speed, unit_filename, bullet_filename)

    def kill(self, other_unit):
        unit_class_name = other_unit. __class__.__name__
        if unit_class_name == 'Hero':
            other_unit.decrease_life()
        else:
            del other_unit
        del self


class Hero(Unit):

    def __init__(self, x, y, angle, bonus=0, speed=0, life_count=3, unit_filename=IMAGE_FILENAME.get('hero', ''),
                 bullet_filename=IMAGE_FILENAME.get('bullet_hero', '')):
        super(Hero, self).__init__(x, y, angle, bonus, speed, unit_filename, bullet_filename)
        self.life_count = life_count

    def decrease_life(self):
        if self.life_count > 1:
            self.life_count -= 1
        else:
            self.life_count = 0
            self.is_dead = True

    def kill(self, other_unit):
        unit_class_name = other_unit. __class__.__name__
        self.decrease_life()
        if unit_class_name == 'Hero':
            other_unit.decrease_life()
        else:
            del other_unit


class Bullet(Unit):
    def __init__(self, unit):
        self.unit_id = id(unit)
        super(Bullet, self).__init__(unit.x, unit.y, unit.angle, 0, unit.speed or DEFAULT_SPEED,
                                     unit.bullet_filename, unit.bullet_filename)

    def kill(self, other_unit):
        unit_class_name = other_unit. __class__.__name__
        if unit_class_name == 'Hero':
            other_unit.decrease_life()
        elif unit_class_name == 'Invader':
            units = get_game_controller().units
            for unit in units:
                if id(unit) == self.unit_id and unit.__class__.name == 'Hero':
                    unit.bonus += other_unit.bonus
            del other_unit
        else:
            del other_unit
        del self


class GameController(object):

    def __init__(self, height, width, invaders_count):
        self.game_field = {'image_filename': IMAGE_FILENAME.get('background', ''), 'height': height, 'width': width}
        self.invaders_count = invaders_count
        self.units = []
        self.set_hero()
        self.set_invaders()

    def set_hero(self):
        pos_x = randint(0, self.game_field['width'])
        pos_y = randint(0, self.game_field['height'])
        angle = randint(0, 360)
        self.units.append(Hero(pos_x, pos_y, angle))

    def set_invaders(self):
        for count in range(self.invaders_count):
            pos_x = randint(0, self.game_field['width'])
            pos_y = randint(0, self.game_field['height'])
            angle = randint(0, 360)
            self.units.append(Invader(pos_x, pos_y, angle))

    def rotate(self, unit_number, angle):
        self.units[unit_number].rotate(angle)

    def change_speed(self, unit_number, speed):
        self.units[unit_number].change_speed(speed)

    def fire(self, unit_number):
        unit = self.units[unit_number]
        self.units.append(Bullet(unit))


@asyncio.coroutine
def run( websocket, path):
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting Space Invaders Game instance.')
    game_object = get_game_controller()

    '''this code for moving invaders. Work as a job.
        We set moving_speed for positive - if reach the left coordinate of our game field
        or negative  - if we reach the right coordinate of our game field '''

    while True:
        _time = 0
        for unit in game_object.units:
            if unit.speed:
                x = round(unit.x0 + unit.speed * _time * math.cos(unit.angle))
                y = round(unit.yo + unit.speed * _time * math.sin(unit.angle) - (g * _time * _time) / 2)
                if x in range(game_object.game_field['height']) and y in range(game_object.game_field['width']):
                    unit.move_to(x, y)
            for obj in game_object.units:
                unit.check_collision(obj)
            yield from websocket.send(unit.to_json())
        yield from asyncio.sleep(TIME_TO_SLEEP)
        _time += TIME_TO_SLEEP
    yield from websocket.close()

