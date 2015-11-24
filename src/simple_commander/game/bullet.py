""" This module describes behaviour of Bullet objects. """

import logging

from simple_commander.game.unit import Unit
from simple_commander.utils.constants import DEFAULT_SPEED_BULLETS


class Bullet(Unit):
    def __init__(self, unit, controller=None):
        self.unit_id = id(unit)
        dimension = unit.get_bullet_dimension()
        super(Bullet, self).__init__(unit.x, unit.y, unit.angle, 0, unit.speed + DEFAULT_SPEED_BULLETS,
                                     unit.bullet_filename, unit.bullet_filename, dimension, controller=controller)

    def reset(self):
        """ Remove bullet. """
        self.kill()
        self.controller.remove_unit(self.id)

    def hit(self, other_unit):
        logging.debug('In hit - %s(%s) and %s(%s)' % (self.__class__.__name__, self.unit_id, other_unit.__class__.__name__, other_unit.id))

        other_unit.bullet_kill(self)


    def change_object(self, x, y, interval):
        pass

    def collision_check(self):
        """ Do we need to check collision for Bullet objects? """
        return False