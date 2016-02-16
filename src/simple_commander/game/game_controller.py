""" This module describes behaviour of Game Controller. """

import asyncio
import json
import logging
from datetime import datetime
from random import randint, shuffle

from simple_commander.game.bullet import Bullet
from simple_commander.game.invader import Invader
from simple_commander.game.hero import Hero
from simple_commander.utils.constants import ANGLE, ACTION_INTERVAL,\
    ROTATION_ANGLE, SPEED, STEP_INTERVAL, UNITS, DEFAULT_LIFE_COUNT


class GameController(object):
    _instance = None
    launched = False
    websockets = {}

    def __init__(self, height=None, width=None, invaders_count=None):
        self.game_field = {'height': height, 'width': width}
        self.invaders_count = invaders_count
        self.units = {}
        self.collisions = {}
        self.random_type = self.get_unit_type()
        self.set_invaders(self.invaders_count)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameController, cls).__new__(cls)
        return cls._instance

    def do_action(self, actions):
        for key in actions:
            action = getattr(self, key)
            hero = self.units.get(actions[key].get('id', ''), '')
            if not action or not hero:
                continue
            if key == 'set_name':
                action(hero, actions[key].get('name', 'user'))
            else:
                asyncio.async(action(hero))

    def new_unit(self, unit_class, *args, **kwargs):
        """ Create new unit. """
        kwargs['controller'] = self
        unit = unit_class(*args, **kwargs)
        self.units[unit.id] = unit
        self.collisions[unit.id] = []
        unit.response('new')
        logging.debug('Create new unit - %s -', unit.__class__.__name__)
        unit.compute_new_coordinate(STEP_INTERVAL)
        return unit

    def drop_connection(self, socket):
        socket = self.websockets[id(socket)]
        self.remove_unit(socket['hero'])
        del socket

    @asyncio.coroutine
    def notify_clients(self, data):
        for key in self.websockets:
            if not self.websockets[key]['socket']._closed:
                data['standings'] = self.get_standings_info()
                self.websockets[key]['socket'].send_str(json.dumps(data))

    def new_hero(self):
        pos_x = randint(0, self.game_field['width'])
        pos_y = randint(0, self.game_field['height'])
        angle = randint(0, 360)
        hero_type = next(self.random_type)
        hero = self.new_unit(Hero, x=pos_x, y=pos_y, angle=angle, obj_type=hero_type['type'],
                             dimension=hero_type['dimension'])
        return hero

    def cleanup_units(self, units):
        """ Remove list of units. """
        for unit in units:
            if unit.is_dead:
                self.remove_unit(unit.id)

    def remove_unit(self, unit_id):
        """ Remove unit with unit ID. """
        unit = self.units.get(unit_id)
        if unit:
            class_name = unit.__class__.__name__
            self.units[unit_id].response('delete')
            del self.units[unit_id]
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
        if len(self.units):
            return {unit: self.units[unit].to_dict() for unit in self.units}
        return {}

    def get_standings_info(self):
        """Return standing information about top 10 user."""
        units = [{'name': unit.name,
                  'type': unit.type,
                  'hits': unit.hits,
                  'deaths': DEFAULT_LIFE_COUNT - unit.life_count,
                  'total': unit.hits - DEFAULT_LIFE_COUNT  + unit.life_count}\
                 for unit in self.units.values() if hasattr(unit, 'life_count')]
        return sorted(units, key=lambda h: (h['total']), reverse=True)[:10]

    @staticmethod
    def set_name(hero, name):
        hero.name = name
        hero.compute_new_coordinate(STEP_INTERVAL)

    @asyncio.coroutine
    def change_speed_up(self, unit):
        self.collisions[unit.id] = []
        unit.change_speed_down_is_pressing = False
        unit.change_speed_up_is_pressing = True
        while unit.change_speed_up_is_pressing and not unit.is_dead:
            new_speed = unit.speed + SPEED
            unit.set_speed(new_speed)
            yield from asyncio.sleep(ACTION_INTERVAL)

    @asyncio.coroutine
    def change_speed_down(self, unit):
        self.collisions[unit.id] = []
        unit.change_speed_up_is_pressing = False
        unit.change_speed_down_is_pressing = True
        while unit.change_speed_down_is_pressing and not unit.is_dead:
            new_speed = unit.speed - SPEED
            unit.set_speed(new_speed)
            yield from asyncio.sleep(ACTION_INTERVAL)

    @asyncio.coroutine
    def stop_change_speed_up(self, unit):
        unit.change_speed_up_is_pressing = False
        unit.compute_new_coordinate(STEP_INTERVAL)

    @asyncio.coroutine
    def stop_change_speed_down(self, unit):
        unit.change_speed_down_is_pressing = False
        unit.compute_new_coordinate(STEP_INTERVAL)

    @asyncio.coroutine
    def start_fire(self, unit):
        unit.is_fire_active = True
        while unit.life_count > 0 and unit.is_fire_active and \
                (datetime.now() - unit.last_fire).total_seconds() >= unit.frequency_fire and not unit.is_dead:
            unit.compute_new_coordinate(unit.frequency_fire)
            self.new_unit(Bullet, unit=unit, controller=self)
            unit.last_fire = datetime.now()
            yield from asyncio.sleep(unit.frequency_fire)

    @asyncio.coroutine
    def stop_fire(self, unit):
        unit.is_fire_active = False

    @asyncio.coroutine
    def rotate_right(self, unit):
        self.collisions[unit.id] = []
        unit.rotate_left_is_pressing = False
        unit.rotate_right_is_pressing = True
        while unit.rotate_right_is_pressing and not unit.is_dead:
            rotate = ANGLE + unit.speed * ROTATION_ANGLE
            new_angle = unit.angle + rotate
            unit.set_angle(new_angle)
            yield from asyncio.sleep(ACTION_INTERVAL)

    @asyncio.coroutine
    def rotate_left(self, unit):
        self.collisions[unit.id] = []
        unit.rotate_right_is_pressing = False
        unit.rotate_left_is_pressing = True
        while unit.rotate_left_is_pressing and not unit.is_dead:
            rotate = ANGLE + unit.speed * ROTATION_ANGLE
            new_angle = unit.angle - rotate
            unit.set_angle(new_angle)
            yield from asyncio.sleep(ACTION_INTERVAL)

    def check_collision(self, unit, interval):
        for key in list(self.units.keys()):
            if self.units.get(unit.id) and self.units.get(key):
                self.units[unit.id].check_collision(self.units[key], interval)

    @asyncio.coroutine
    def stop_rotate_right(self, unit):
        unit.rotate_right_is_pressing = False
        unit.compute_new_coordinate(STEP_INTERVAL)

    @asyncio.coroutine
    def stop_rotate_left(self, unit):
        unit.rotate_left_is_pressing = False
        unit.compute_new_coordinate(STEP_INTERVAL)

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
                yield from asyncio.sleep(STEP_INTERVAL)