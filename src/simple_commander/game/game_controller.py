""" This module describes behaviour of Game Controller. """

import asyncio
import json
import logging
from random import randint, shuffle

from simple_commander.game.bullet import Bullet
from simple_commander.game.invader import Invader
from simple_commander.game.hero import Hero
from simple_commander.utils.constants import STEP_INTERVAL, UNITS


class GameController(object):
    _instance = None
    launched = False
    websockets = {}

    def __init__(self, height=None, width=None, invaders_count=None):
        self.game_field = {'height': height, 'width': width}
        self.invaders_count = invaders_count
        self.units = {}
        self.random_type = self.get_unit_type()
        self.set_invaders(self.invaders_count)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameController, cls).__new__(cls)
        return cls._instance

    def action(self, data):
        for key in data:
            action = getattr(self, key)
            hero = self.units.get(data[key].get('id', ''), '')
            if not action or not hero:
                continue
            if key == 'set_name':
                action(hero, data[key].get('name', 'user'))
            else:
                action(hero)

    def new_unit(self, unit_class, *args, **kwargs):
        kwargs['controller'] = self
        unit = unit_class(*args, **kwargs)
        self.units[unit.id] = unit
        unit.response('new')
        unit.compute_new_coordinate(STEP_INTERVAL)
        return unit

    def drop_connection(self, socket):
        socket = self.websockets[id(socket)]
        self.remove_unit(socket['hero'])
        del socket

    @asyncio.coroutine
    def notify_clients(self, data):
        if self.websockets:
            for key in self.websockets:
                if not self.websockets[key]['socket']._closed:
                    self.websockets[key]['socket'].send_str(json.dumps(data))

    def new_hero(self):
        pos_x = randint(0, self.game_field['width'])
        pos_y = randint(0, self.game_field['height'])
        angle = randint(0, 360)
        hero_type = next(self.random_type)
        hero = self.new_unit(Hero, x=pos_x, y=pos_y, angle=angle, obj_type=hero_type['type'],
                             dimension=hero_type['dimension'])
        return hero

    def check_if_remove_units(self, units):
        for unit in units:
            if unit.is_dead:
                self.remove_unit(unit.id)

    def remove_unit(self, obj_id):
        if self.units[obj_id]:
            class_name = self.units[obj_id].__class__.__name__
            self.units[obj_id].response('delete')
            del self.units[obj_id]
            if class_name == 'Invader':
                self.set_invaders(1)

    def start(self, socket, data, *args, **kwargs):
        asyncio.async(self.run())
        my_hero = self.new_hero()
        self.websockets[id(socket)] = {'socket': socket, 'hero': my_hero.id}
        name = data.get('name', 'user')
        self.set_name(my_hero, name)
        start_conditions = {'init': {
            'hero_id': my_hero.id,
            'game': self.game_field,
            'units': self.get_units(),
            'frequency': STEP_INTERVAL}}
        socket.send_str(json.dumps(start_conditions))

    def add_hits(self, bullet):
        for unit in self.units:
            if id(self.units[unit]) == bullet.unit_id and isinstance(self.units[unit], Hero):
                self.units[unit].hits += 1

    @staticmethod
    def get_unit_type():
        i = -1
        types = UNITS['hero'][:]
        shuffle(types)
        while True:
            i += 1
            yield types[i]
            if i == len(types)-1:
                shuffle(types)
                i = -1

    def set_invaders(self, count):
        for count in range(count):
            pos_x = randint(0, self.game_field['width'])
            pos_y = randint(0, self.game_field['height'])
            angle = randint(0, 360)
            speed = randint(30, 70)
            self.new_unit(Invader, x=pos_x, y=pos_y, angle=angle, speed=speed)

    def get_units(self):
        units = []
        if len(self.units):
            units = {unit: self.units[unit].to_dict() for unit in self.units}
        return units

    @staticmethod
    def set_name(hero, name):
        hero.name = name
        hero.compute_new_coordinate(STEP_INTERVAL)

    @staticmethod
    def change_speed_up(hero):
        hero.change_speed_is_pressing = True
        asyncio.async(hero.change_speed('up'))

    @staticmethod
    def change_speed_down(hero):
        hero.change_speed_is_pressing = True
        asyncio.async(hero.change_speed('down'))

    @staticmethod
    def stop_change_speed(hero):
        hero.change_speed_is_pressing = False
        hero.compute_new_coordinate(STEP_INTERVAL)

    @staticmethod
    def start_fire(hero):
        hero.fire_is_pressing = True
        asyncio.async(hero.fire(Bullet))

    @staticmethod
    def stop_fire(hero):
        hero.fire_is_pressing = False

    @staticmethod
    def rotate_right(hero):
        hero.rotate_is_pressing = True
        asyncio.async(hero.rotate('right'))

    @staticmethod
    def rotate_left(hero):
        hero.rotate_is_pressing = True
        asyncio.async(hero.rotate('left'))

    @staticmethod
    def stop_rotate(hero):
        hero.rotate_is_pressing = False
        hero.compute_new_coordinate(STEP_INTERVAL)

    @asyncio.coroutine
    def run(self):
        if not self.launched:
            self.launched = True
            logging.basicConfig(level=logging.DEBUG)
            logging.info('Starting Space Invaders Game instance.')

            '''this code for moving invaders. Work as a job.
                We set moving_speed for positive - if reach the left coordinate of our game field
                or negative  - if we reach the right coordinate of our game field '''
            while len(self.units) > 0:
                for unit in list(self.units.keys()):
                    if self.units.get(unit):
                        if self.units[unit].speed:
                            self.units[unit].compute_new_coordinate(STEP_INTERVAL)
                        for key in list(self.units.keys()):
                            if self.units.get(unit) and self.units.get(key):
                                self.units[unit].check_collision(self.units[key])
                yield from asyncio.sleep(STEP_INTERVAL)