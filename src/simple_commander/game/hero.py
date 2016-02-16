""" This module describes behaviour of Hero objects. """
import asyncio
import logging
import math

from datetime import datetime
from random import randint

from simple_commander.game.unit import Unit
from simple_commander.utils.constants import STEP_INTERVAL, UNITS


class Hero(Unit):

    def __init__(self, x, y, angle, hits=0, speed=0, life_count=3, frequency_fire=0.5, obj_type='',
                 bullet_type=UNITS.get('bullet_hero', {}).get('type', ''), dimension=0, controller=None):
        if not obj_type and len(UNITS.get('hero', [])):
            random_number = randint(0, len(UNITS.get('hero', [])) - 1)
            obj_type = UNITS.get('hero', [])[random_number].get('type', '')
            dimension = UNITS.get('hero', [])[random_number].get('dimension', '')
        super(Hero, self).__init__(x, y, angle, hits, speed, obj_type, bullet_type, dimension, controller=controller)
        self.frequency_fire = frequency_fire
        self.last_fire = datetime.now()
        self.life_count = life_count
        self.name = None

    def set_to_new_position(self):
        pos_x = randint(0, self.controller.game_field['width'])
        pos_y = randint(0, self.controller.game_field['height'])
        angle = randint(0, 360)
        self.x = pos_x
        self.y = pos_y
        self.x1 = pos_x
        self.y1 = pos_y
        self.angle = angle
        self.speed = 0
        self.response('update')

    def decrease_life(self):
        if self.life_count > 1:
            self.life_count -= 1
            self.response("delete")
            self.set_to_new_position()
            self.response("new")
        else:
            self.life_count = 0
            self.kill()
        self.response('update_life')

    def reset(self):
        self.speed = 0
        self.x = self.x1
        self.y = self.y1
        self.response('update')

    def hit(self, other_unit):
        logging.debug('In hit - %s and %s' % (self.__class__.__name__, other_unit.__class__.__name__))
        self.hits += 1
        self.decrease_life()
        if other_unit is Hero:
            other_unit.hits += 1
            other_unit.decrease_life()
        else:
            # Add hits if other_unit is Bullet
            if not other_unit.collision_check():
                self.controller.add_hits(other_unit)
            other_unit.kill()

    @asyncio.coroutine
    def change_object(self, x, y, interval, time_to_crash):
        """ Recalculate speed for Hero object. """
        self.speed = round(math.sqrt((x - self.x1) ** 2 + (y - self.y1) ** 2) / interval)
        self.move_to(x, y)

    def collision_check(self):
        """ Do we need to check collision for Hero objects? """
        return True

    def get_bullet_dimension(self):
        """ Get dimension for Hero object. """
        return UNITS.get('bullet_hero', {}).get('dimension', 0)

    def bullet_kill(self, obj_kill):
        """ Kill object after bullet hit. """
        obj_kill.controller.add_hits(obj_kill)
        self.decrease_life()
        obj_kill.kill()