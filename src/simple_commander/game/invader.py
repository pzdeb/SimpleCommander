"""This module describes Invader's behaviour. """

import logging
from random import randint

from simple_commander.game.unit import Unit
from simple_commander.utils.constants import DEFAULT_SPEED, STEP_INTERVAL, UNITS


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
        self.angle = randint(0, 360)
        self.compute_new_coordinate(STEP_INTERVAL)
        logging.debug('Reset %s angle. New angle - %s' % (self.__class__.__name__, self.angle))

    def hit(self, other_unit):
        pass

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