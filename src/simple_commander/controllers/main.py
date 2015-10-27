#!/usr/bin/env python3
import asyncio
import datetime
import json
import uuid

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

DEFAULT_SPEED = 35
STEP_INTERVAL = 1  # 1 second, can be changed to 0.5
UNIT_PROPERTIES = ['x0', 'y0', 'x1', 'y1', 'angle', 'bonus', 'speed', 'id', 'life_count']


class Unit(object):

    def __init__(self, x, y, angle, bonus, speed, unit_filename, bullet_filename):
        self.image_filename = unit_filename
        self.bullet_filename = bullet_filename
        self.time_last_calculation = datetime.datetime.now()
        self.x0 = x
        self.y0 = y
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.width = 10  # temporary when we don't have real images
        self.height = 10  # must be height of real image
        self.bonus = bonus
        self.speed = speed
        self.id = str(uuid.uuid4())
        self.is_dead = False
        self.shift = 5

    def to_dict(self):
        result = {}
        for attr in self.__dict__:
            if attr in UNIT_PROPERTIES:
                result[attr] = self.__dict__[attr]
        return result

    def translate(self, x, y, game_field):
        y = game_field.get('height', 0) - y
        return x, y

    def compute_new_coordinate(self, game_field, force=None):
        min_height = int(0 + self.height / 2)
        min_width = int(0 + self.width / 2)
        max_height = int(game_field.get('height', 0) - self.height / 2)
        max_width = int(game_field.get('width', 0) - self.width / 2)
        if force and (datetime.datetime.now() - self.time_last_calculation).total_seconds() < STEP_INTERVAL:
            interval = (datetime.datetime.now() - self.time_last_calculation).total_seconds()
        else:
            interval = STEP_INTERVAL
        x0, y0 = self.translate(self.x1, self.y1, game_field)
        x = round(x0 + self.speed * interval * math.sin(round(math.radians(self.angle), 2)))
        y = round(y0 + self.speed * interval * math.cos(round(math.radians(self.angle), 2)))
        x, y = self.translate(x, y, game_field)
        self.time_last_calculation = datetime.datetime.now()
        if x in range(min_width, max_width) and y in range(min_height, max_height):
            self.move_to(x, y)
        else:
            self.reset()

    def move_to(self, x, y):
        logging.info('Move %s to new coordinate - (%s, %s)' % (self.__class__.__name__, x, y))
        self.x0 = self.x1
        self.y0 = self.y1
        self.x1 = x
        self.y1 = y

    def rotate(self, angle):
        logging.info('Rotate %s from %s degree to %s degree' % (self.__class__.__name__, self.angle, self.angle+angle))
        self.angle += angle

    def change_speed(self, speed):
        new_speed = self.speed + speed
        self.speed = new_speed > 0 and new_speed or 0
        logging.info('Change %s speed to %s' % (self.__class__.__name__, self.speed))

    def check_collision(self, other_unit, all_units, height, width):
        # check if coordinate for two units is the same
        # for this check we also include width and height of unit's image
        # (other_unit.x - other_unit.width / 2 < self.x < other_unit.x + other_unit.width / 2)
        # (other_unit.y - other_unit.height / 2 < self.y < other_unit.y + other_unit.height / 2)
        if id(self) != id(other_unit) and getattr(self, 'unit_id', '') != id(other_unit) and \
                getattr(other_unit, 'unit_id', '') != id(self):
            if (self.x1 > other_unit.x1 - other_unit.width / 2) and (self.x1 < other_unit.x1 + other_unit.width / 2) and \
                    (self.y1 > other_unit.y1 - other_unit.height / 2) and (self.y1 < other_unit.y1 + other_unit.height / 2):
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
        logging.info('Reset %s angle. New angle - %s' % (self.__class__.__name__, self.angle))

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        logging.info('In kill - %s and %s' % (self.__class__.__name__, unit_class_name))
        if unit_class_name == 'Hero':
            other_unit.decrease_life(units)
        else:
            other_unit.is_dead = True
            del units[other_unit.id]
        self.is_dead = True
        del units[self.id]


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
        logging.info('In kill - %s and %s' % (self.__class__.__name__, unit_class_name))
        self.decrease_life(units)
        if unit_class_name == 'Hero':
            other_unit.decrease_life(units)
        else:
            other_unit.is_dead = True
            del units[other_unit.id]


class Bullet(Unit):
    def __init__(self, unit):
        self.unit_id = id(unit)
        super(Bullet, self).__init__(unit.x0, unit.y0, unit.angle, 0, unit.speed * 2 or DEFAULT_SPEED,
                                     unit.bullet_filename, unit.bullet_filename)

    def reset(self):
        self.is_dead = True
        game = GameController(get_old=True)
        if game.units.get(self.id, ''):
            del game.units[self.id]

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        logging.info('In kill - %s and %s' % (self.__class__.__name__, unit_class_name))
        if unit_class_name == 'Hero':
            other_unit.decrease_life()
        elif unit_class_name == 'Invader':
            for unit in units:
                if id(units[unit]) == self.unit_id and units[unit].__class__.__name__ == 'Hero':
                    units[unit].bonus += other_unit.bonus
                    logging.info('Add %s bonus for %s. Now he has %s bonus'
                                 % (other_unit.bonus, unit.__class__.__name__, unit.bonus))
            other_unit.is_dead = True
            del units[other_unit.id]
        else:
            other_unit.is_dead = True
        self.is_dead = True
        del units[self.id]


class GameController(object):
    _instance = None
    _launched = False

    def __init__(self, height=None, width=None, invaders_count=None, notify_clients=None, get_old=False):
        if get_old:
            return
        self.game_field = {'image_filename': IMAGE_FILENAME.get('background', ''), 'height': height, 'width': width}
        self.invaders_count = invaders_count
        self.units = {}
        self.set_invaders()
        self.notify_clients = notify_clients

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameController, cls).__new__(cls)
        return cls._instance

    def set_hero(self):
        pos_x = randint(0, self.game_field['width'])
        pos_y = randint(0, self.game_field['height'])
        angle = randint(0, 360)
        hero = Hero(pos_x, pos_y, angle)
        self.units[hero.id] = hero
        return hero

    def set_invaders(self):
        for count in range(self.invaders_count):
            pos_x = randint(0, self.game_field['width'])
            pos_y = randint(0, self.game_field['height'])
            angle = randint(0, 360)
            invader = Invader(pos_x, pos_y, angle)
            self.units[invader.id] = invader

    def fire(self, unit):
        logging.info('Fire!! Creating bullet!')
        bullet = Bullet(unit)
        self.units[bullet.id] = bullet

    def get_serialized_units(self):
        units = []
        if len(self.units):
            units = {unit: self.units[unit].to_dict() for unit in self.units}
        return json.dumps(units)

    @asyncio.coroutine
    def run(self, loop=True):
        if not self._launched or not loop:
            self._launched = True
            logging.basicConfig(level=logging.DEBUG)
            logging.info('Starting Space Invaders Game instance.')

            '''this code for moving invaders. Work as a job.
                We set moving_speed for positive - if reach the left coordinate of our game field
                or negative  - if we reach the right coordinate of our game field '''

            while loop:
                for unit in list(self.units.keys()):
                    if self.units.get(unit):
                        if self.units[unit].speed:
                            self.units[unit].compute_new_coordinate(self.game_field)
                        for key in list(self.units.keys()):
                            if self.units.get(unit) and self.units.get(key):
                                self.units[unit].check_collision(self.units[key], self.units, self.game_field['height'],
                                                                 self.game_field['width'])
                yield from self.notify_clients(self.get_serialized_units())
                yield from asyncio.sleep(STEP_INTERVAL)