#!/usr/bin/env python3
import asyncio
import json

import logging

import math

from random import randint

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
TIME_TO_SLEEP = 1  # 1 second, can be changed to 0.5
g = 9.81


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
        self.step = 0
        self.shift = 5

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def compute_new_coordinate(self, game_field):
        max_height = game_field.get('height', 0)
        max_width = game_field.get('width', 0)
        self.step += TIME_TO_SLEEP
        print ('self.speed - ', self.speed)
        x = round(self.x0 + self.speed * round(self.step) * math.cos(self.angle))
        y = round(self.y0 + self.speed * round(self.step) * math.sin(self.angle) - (g * self.step * self.step) / 2)
        if x in range(-max_height, max_height) and y in range(-max_width, max_width):
            self.move_to(x, y)
        else:
            self.reset()

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def rotate(self, angle):
        self.angle += angle

    def change_speed(self, speed):
        new_speed = self.speed + speed
        self.speed = new_speed > 0 and new_speed or 0

    def check_collision(self, other_unit, all_units):
        # check if coordinate for two units is the same
        # for this check we also include width and height of unit's image
        # (other_unit.x - other_unit.width / 2 < self.x < other_unit.x + other_unit.width / 2)
        # (other_unit.y - other_unit.height / 2 < self.y < other_unit.y + other_unit.height / 2)
        if id(self) != id(other_unit) and getattr(self, 'unit_id', '') != id(other_unit) and \
                getattr(other_unit, 'unit_id', '') != id(self):
            if (self.x > other_unit.x - other_unit.width / 2) and (self.x < other_unit.x + other_unit.width / 2) and \
                    (self.y > other_unit.y - other_unit.height / 2) and (self.y < other_unit.y + other_unit.height / 2):
                self.kill(other_unit, all_units)

    def reset(self):
        raise NotImplementedError

    def kill(self, other_unit, units):
        raise NotImplementedError


class Invader(Unit):

    def __init__(self, x, y, angle, bonus=10, speed=DEFAULT_SPEED, unit_filename='',
                 bullet_filename=IMAGE_FILENAME.get('bullet_invader', '')):
        if not unit_filename and len(IMAGE_FILENAME.get('invader', [])):
            random_number = randint(0, len(IMAGE_FILENAME.get('invader', [])) - 1)
            unit_filename = IMAGE_FILENAME.get('invader', [])[random_number]
        super(Invader, self).__init__(x, y, angle, bonus, speed, unit_filename, bullet_filename)

    def reset(self):
        self.angle = randint(0, 360)
        self.step = 0
        self.x0 = self.x
        self.y0 = self.y

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        if unit_class_name == 'Hero':
            other_unit.decrease_life(units)
        else:
            other_unit.is_dead = True
            units.remove(other_unit)
        self.is_dead = True
        units.remove(self)


class Hero(Unit):

    def __init__(self, x, y, angle, bonus=0, speed=0, life_count=3, unit_filename=IMAGE_FILENAME.get('hero', ''),
                 bullet_filename=IMAGE_FILENAME.get('bullet_hero', '')):
        super(Hero, self).__init__(x, y, angle, bonus, speed, unit_filename, bullet_filename)
        self.life_count = life_count

    def decrease_life(self, units):
        if self.life_count > 1:
            self.life_count -= 1
        else:
            self.life_count = 0
            self.is_dead = True
            units.remove(self)

    def reset(self):
        self.speed = 0

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        self.decrease_life(units)
        if unit_class_name == 'Hero':
            other_unit.decrease_life(units)
        else:
            other_unit.is_dead = True
            units.remove(other_unit)


class Bullet(Unit):
    def __init__(self, unit):
        self.unit_id = id(unit)
        super(Bullet, self).__init__(unit.x, unit.y, unit.angle, 0, unit.speed * 2 or DEFAULT_SPEED,
                                     unit.bullet_filename, unit.bullet_filename)

    def reset(self):
        self.is_dead = True

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        if unit_class_name == 'Hero':
            other_unit.decrease_life()
        elif unit_class_name == 'Invader':
            for unit in units:
                if id(unit) == self.unit_id and unit.__class__.__name__ == 'Hero':
                    unit.bonus += other_unit.bonus
            other_unit.is_dead = True
            units.remove(other_unit)
        else:
            other_unit.is_dead = True
        self.is_dead = True
        units.remove(self)


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

    def fire(self, unit):
        self.units.append(Bullet(unit))

    @asyncio.coroutine
    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.info('Starting Space Invaders Game instance.')

        '''this code for moving invaders. Work as a job.
            We set moving_speed for positive - if reach the left coordinate of our game field
            or negative  - if we reach the right coordinate of our game field '''

        while True:
            for unit in self.units:
                if unit.speed:
                    unit.compute_new_coordinate(self.game_field)
                for obj in self.units:
                    unit.check_collision(obj, self.units)
            yield from asyncio.sleep(TIME_TO_SLEEP)
