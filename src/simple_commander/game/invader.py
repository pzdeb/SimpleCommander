"""This module describes Invader's behaviour. """

import logging
from random import randint
from datetime import datetime

from simple_commander.utils.utils import float_range
from simple_commander.game.unit import Unit
from simple_commander.utils.constants import DEFAULT_SPEED, STEP_INTERVAL, UNITS
from simple_commander.game.bullet import Bullet


class Invader(Unit):

    def __init__(self, x, y, angle, hits=10, speed=DEFAULT_SPEED, obj_type='',
                 bullet_type=UNITS.get('bullet_invader', {}).get('type', ''), dimension=0, controller=None):
        if not obj_type and len(UNITS.get('invader', [])):
            random_number = randint(0, len(UNITS.get('invader', [])) - 1)
            obj_type = UNITS.get('invader', [])[random_number].get('type', '')
            dimension = UNITS.get('invader', [])[random_number].get('dimension', '')
        super(Invader, self).__init__(x, y, angle, hits, speed, obj_type, bullet_type, dimension, controller=controller)

    def reset(self):
        #TODO: add angle into account
        logging.debug('Reset %s angle. New angle - %s' % (self.__class__.__name__, self.angle))

    def hit(self, other_unit):
        unit_class_name = other_unit. __class__.__name__
        logging.debug('In hit - %s and %s' % (self.__class__.__name__, unit_class_name))
        if unit_class_name == 'Hero':
            other_unit.hits += 1
            other_unit.decrease_life()
            self.kill()
        elif isinstance(other_unit, Bullet):
            self.controller.add_hits(other_unit)
            other_unit.kill()
            self.kill()

    def change_object(self, x, y, interval):
        """ Reset Invader object. """
        self.reset()

    def collision_check(self):
        """ Do we need to check collision for Invader objects? """
        return True

    def get_bullet_dimension(self):
        """ Get dimension for Invader object. """
        return UNITS.get('bullet_invader', {}).get('dimension', 0)

    def bullet_kill(self, obj_kill):
        """ Kill object after bullet hit. """
        obj_kill.controller.add_hits(obj_kill)
        self.kill()
        obj_kill.kill()

    def compute_new_coordinate(self, interval):
        time_from_last_calculate = (datetime.now() - self.time_last_calculation).total_seconds()
        # Calculate real position
        if time_from_last_calculate < STEP_INTERVAL:
            x = self.calculate_abscissa(self.x, time_from_last_calculate)
            y = self.calculate_ordinate(self.y, time_from_last_calculate)
            self.x1, self.y1 = self.set_in_limit(x, y)

        # Calculate future position
        x = self.calculate_abscissa(self.x1, interval)
        y = self.calculate_ordinate(self.y1, interval)

        self.time_last_calculation = datetime.now()
        if float_range(x, self.min_width, self.max_width) and float_range(y, self.min_height, self.max_height):
            self.move_to(x, y)
        else:
            self.angle = (self.angle + 90) % 360
            x = self.calculate_abscissa(self.x1, interval)
            y = self.calculate_ordinate(self.y1, interval)
            x, y = self.set_in_limit(x, y)
            self.move_to(x, y)
        self.controller.check_collision(self, interval)
