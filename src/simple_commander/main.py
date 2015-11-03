#!/usr/bin/env python3
import asyncio
import uuid
from datetime import datetime

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

UNITS = {'invader': [{'type': 'invader1', 'dimension': 50},
                     {'type': 'invader2', 'dimension': 50},
                     {'type': 'invader3', 'dimension': 46}],
         'hero': [{'type': 'hero1', 'dimension': 52},
                  {'type': 'hero2', 'dimension': 44},
                  {'type': 'hero3', 'dimension': 53}],
         'bullet_hero': {'type': 'bullet_hero', 'dimension': 10},
         'bullet_invader': {'type': 'bullet_invader', 'dimension': 10}}

ANGLE = 2
DEFAULT_SPEED = 35
SPEED = 2
STEP_INTERVAL = 1  # 1 second, can be changed to 0.5
ACTION_INTERVAL = 0.05
UNIT_PROPERTIES = ['x', 'y', 'x1', 'y1', 'angle', 'bonus', 'speed', 'id', 'life_count', 'type']
MAX_ANGLE = 360


class Unit(object):

    def __init__(self, x, y, angle, bonus, speed, type, bullet_type, dimension, controller=None):
        self.controller = controller
        self.type = type
        self.bullet_filename = bullet_type
        self.time_last_calculation = datetime.now()
        self.x = x
        self.y = y
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.width = dimension
        self.height = dimension
        self.bonus = bonus
        self.speed = speed
        self.id = str(uuid.uuid4())
        self.is_dead = False
        self.shift = 5
        self.stop_rotate = 'stop'
        self.stop_change_speed = 'stop'

    def response(self, action, **kwargs):
        if not self.controller:
            return
        data = {action: self.to_dict()}
        data[action].update(kwargs)
        asyncio.async(self.controller.notify_clients(data))

    def to_dict(self):
        result = {}
        for attr in self.__dict__:
            if attr in UNIT_PROPERTIES:
                result[attr] = self.__dict__[attr]
        return result

    def translate(self, x, y, game_field):
        y = game_field.get('height', 0) - y
        return x, y

    def compute_new_coordinate(self, game_field, interval):
        min_height = int(0 + self.height / 2)
        min_width = int(0 + self.width / 2)
        max_height = int(game_field.get('height', 0) - self.height / 2)
        max_width = int(game_field.get('width', 0) - self.width / 2)

        # Calculate real position
        time_from_last_calculate = (datetime.now() - self.time_last_calculation).total_seconds()
        x0, y0 = self.translate(self.x, self.y, game_field)
        x = round(x0 + self.speed * time_from_last_calculate * math.sin(round(math.radians(self.angle), 2)))
        y = round(y0 + self.speed * time_from_last_calculate * math.cos(round(math.radians(self.angle), 2)))
        self.x1, self.y1 = self.translate(x, y, game_field)

        # Calculate future position
        x0, y0 = self.translate(self.x1, self.y1, game_field)
        x = round(x0 + self.speed * interval * math.sin(round(math.radians(self.angle), 2)))
        y = round(y0 + self.speed * interval * math.cos(round(math.radians(self.angle), 2)))
        x, y = self.translate(x, y, game_field)

        self.time_last_calculation = datetime.now()
        if x in range(min_width, max_width) and y in range(min_height, max_height):
            self.move_to(x, y)
        else:
            self.reset(game_field)

    def move_to(self, x, y):
        logging.info('Move %s to new coordinate - (%s, %s)' % (self.__class__.__name__, x, y))
        self.x = self.x1
        self.y = self.y1
        self.x1 = x
        self.y1 = y
        self.response('update', frequency=STEP_INTERVAL)

    @asyncio.coroutine
    def rotate(self, side):
        while self.stop_rotate != 'stop':
            new_angle = self.angle + ANGLE if side == 'right' else self.angle - ANGLE
            if new_angle > MAX_ANGLE:
                new_angle -= MAX_ANGLE
            elif new_angle < 0:
                new_angle += MAX_ANGLE
            logging.info('Rotate %s from %s degree to %s degree' % (self.__class__.__name__, self.angle, new_angle))
            self.angle = new_angle
            self.compute_new_coordinate(self.controller.game_field, ACTION_INTERVAL)
            yield from asyncio.sleep(ACTION_INTERVAL)

    def change_speed(self, direct):
        while self.stop_change_speed != 'stop':
            new_speed = self.speed + SPEED if direct == 'front' else self.speed - SPEED
            self.speed = new_speed > 0 and new_speed or 0
            logging.info('Change %s speed to %s' % (self.__class__.__name__, self.speed))
            self.compute_new_coordinate(self.controller.game_field, ACTION_INTERVAL)
            yield from asyncio.sleep(ACTION_INTERVAL)

    def check_collision(self, other_unit, all_units):
        # check if coordinate for two units is the same
        # for this check we also include width and height of unit's image
        # (other_unit.x - other_unit.width / 2 < self.x < other_unit.x + other_unit.width / 2)
        # (other_unit.y - other_unit.height / 2 < self.y < other_unit.y + other_unit.height / 2)
        if id(self) != id(other_unit) and getattr(self, 'unit_id', '') != id(other_unit) and \
                getattr(other_unit, 'unit_id', '') != id(self):
            if (self.x1 > other_unit.x1 - other_unit.width / 2) and (self.x1 < other_unit.x1 + other_unit.width / 2) and \
                    (self.y1 > other_unit.y1 - other_unit.height / 2) and (self.y1 < other_unit.y1 + other_unit.height / 2):
                self.kill(other_unit, all_units)  

    def reset(self, game_field):
        raise NotImplementedError

    def kill(self, other_unit, units):
        raise NotImplementedError


class Invader(Unit):

    def __init__(self, x, y, angle, bonus=10, speed=DEFAULT_SPEED, type='',
                 bullet_type=UNITS.get('bullet_invader', {}).get('type', ''), dimension=0, controller=None):
        if not type and len(UNITS.get('invader', [])):
            random_number = randint(0, len(UNITS.get('invader', [])) - 1)
            type = UNITS.get('invader', [])[random_number].get('type', '')
            dimension = UNITS.get('invader', [])[random_number].get('dimension', '')
        super(Invader, self).__init__(x, y, angle, bonus, speed, type, bullet_type, dimension, controller=controller)

    def reset(self, game_field):
        self.angle = randint(0, 360)
        self.compute_new_coordinate(game_field, STEP_INTERVAL)
        logging.info('Reset %s angle. New angle - %s' % (self.__class__.__name__, self.angle))

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        logging.info('In kill - %s and %s' % (self.__class__.__name__, unit_class_name))
        if unit_class_name == 'Hero':
            other_unit.decrease_life(units)
            other_unit.response('update')
        else:
            other_unit.is_dead = True
            del units[other_unit.id]
            other_unit.response('delete')
        self.is_dead = True
        del units[self.id]
        self.response('delete')


class Hero(Unit):

    def __init__(self, x, y, angle, bonus=0, speed=0, life_count=3, type='',
                 bullet_type=UNITS.get('bullet_hero', {}).get('type', ''), dimension=0, controller=None):
        if not type and len(UNITS.get('hero', [])):
            random_number = randint(0, len(UNITS.get('hero', [])) - 1)
            type = UNITS.get('hero', [])[random_number].get('type', '')
            dimension = UNITS.get('hero', [])[random_number].get('dimension', '')
        super(Hero, self).__init__(x, y, angle, bonus, speed, type, bullet_type, dimension, controller=controller)
        self.life_count = life_count

    def decrease_life(self, units):
        if self.life_count > 1:
            self.life_count -= 1
        else:
            self.life_count = 0
            self.is_dead = True
            units.remove(self)

    def reset(self, game_field):
        self.speed = 0
        self.x = self.x1
        self.y = self.y1
        self.response('update')

    def kill(self, other_unit, units):
        unit_class_name = other_unit. __class__.__name__
        logging.info('In kill - %s and %s' % (self.__class__.__name__, unit_class_name))
        self.decrease_life(units)
        if unit_class_name == 'Hero':
            other_unit.decrease_life(units)
            self.response('update')
        else:
            other_unit.is_dead = True
            del units[other_unit.id]
            other_unit.response('delete')


class Bullet(Unit):
    def __init__(self, unit, controller=None):
        self.unit_id = id(unit)
        dimension = unit.__class__.__name__ == 'Hero' and UNITS.get('bullet_hero', {}).get('dimension', 0)\
            or UNITS.get('bullet_invader', {}).get('dimension', 0)
        super(Bullet, self).__init__(unit.x0, unit.y0, unit.angle, 0, unit.speed * 2 or DEFAULT_SPEED,
                                     unit.bullet_type, unit.bullet_type, dimension, controller=controller)

    def reset(self, game_field):
        self.is_dead = True
        if self.controller.units.get(self.id, ''):
            del self.controller.units[self.id]

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


__game = None

def get_game(height=None, width=None, invaders_count=None, notify_clients=None):
    global __game

    if not __game and height and width and invaders_count is not None:
        __game = GameController(height=height,
                                width=width,
                                invaders_count=invaders_count,
                                notify_clients=notify_clients)
    return __game

class GameController(object):
    _instance = None
    _launched = False

    def __init__(self, height=None, width=None, invaders_count=None, notify_clients=None):
        self.game_field = {'height': height, 'width': width}
        self.notify_clients = notify_clients
        self.invaders_count = invaders_count
        self.units = {}
        self.set_invaders()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameController, cls).__new__(cls)
        return cls._instance

    def new_unit(self, unit_class, *args, **kwargs):
        kwargs['controller'] = self
        unit = unit_class(*args, **kwargs)
        self.units[unit.id] = unit
        unit.response('new')
        return unit

    def new_hero(self):
        pos_x = randint(0, self.game_field['width'])
        pos_y = randint(0, self.game_field['height'])
        angle = randint(0, 360)
        hero = self.new_unit(Hero, x=pos_x, y=pos_y, angle=angle)
        return hero

    def set_invaders(self):
        for count in range(self.invaders_count):
            pos_x = randint(0, self.game_field['width'])
            pos_y = randint(0, self.game_field['height'])
            angle = randint(0, 360)
            self.new_unit(Invader, x=pos_x, y=pos_y, angle=angle)

    def fire(self, unit):
        logging.info('Fire!! Creating bullet!')
        bullet = self.new_unit(Bullet, unit=unit, controller=self)
        self.new_unit(bullet)

    def get_units(self):
        units = []
        if len(self.units):
            units = {unit: self.units[unit].to_dict() for unit in self.units}
        return units

    @asyncio.coroutine
    def run(self):
        if not self._launched:
            self._launched = True
            logging.basicConfig(level=logging.DEBUG)
            logging.info('Starting Space Invaders Game instance.')

            '''this code for moving invaders. Work as a job.
                We set moving_speed for positive - if reach the left coordinate of our game field
                or negative  - if we reach the right coordinate of our game field '''
            while True:
                for unit in list(self.units.keys()):
                    if self.units.get(unit):
                        if self.units[unit].speed and (datetime.now() -
                                                       self.units[unit].time_last_calculation).total_seconds() >= STEP_INTERVAL:
                            self.units[unit].compute_new_coordinate(self.game_field, STEP_INTERVAL)
                        for key in list(self.units.keys()):
                            if self.units.get(unit) and self.units.get(key):
                                self.units[unit].check_collision(self.units[key], self.units)
                yield from asyncio.sleep(STEP_INTERVAL)