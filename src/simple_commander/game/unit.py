"""Base module for all units. """
import asyncio
import logging
import math
import uuid
from datetime import datetime

from simple_commander.utils.utils import float_range
from simple_commander.utils.constants import ACTION_INTERVAL, ANGLE, MAX_ANGLE, \
                                             MAX_ANGLE, MAX_SPEED, ROTATION_ANGLE, \
                                             SPEED, STEP_INTERVAL, UNIT_PROPERTIES
from simple_commander.utils.line_intersection import object_intersection, point_distance


class Unit(object):
    """ Base class for all the units. """

    def __init__(self, x, y, angle, hits, speed, obj_type, bullet_type, dimension, controller=None):
        """ Basic initialization. """
        self.controller = controller
        self.type = obj_type
        self.bullet_filename = bullet_type
        self.time_last_calculation = datetime.now()
        self.x = x
        self.y = y
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.width = dimension
        self.height = dimension
        self.hits = hits
        self.speed = speed
        self.id = str(uuid.uuid4())
        self.is_dead = False
        self.shift = 5
        self.rotate_is_pressing = False
        self.change_speed_is_pressing = False
        self.min_height = float(self.height / 2)
        self.min_width = float(self.width / 2)
        self.max_height = float(self.controller.game_field.get('height', 0) - self.height / 2)
        self.max_width = float(self.controller.game_field.get('width', 0) - self.width / 2)

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

    def set_in_limit(self, x, y):
        x = min(max(x, self.min_width), self.max_width)
        y = min(max(y,  self.min_height), self.max_height)
        return x, y

    def calculate_abscissa(self, point, interval):
        """ Calculate abscissa for point with interval. """
        res = round(point + self.speed * interval * math.sin(round(math.radians(180 - self.angle), 2)))
        return res

    def calculate_ordinate(self, point, interval):
        """ Calculate ordinate for point with interval. """
        res = round(point + self.speed * interval * math.cos(round(math.radians(180 - self.angle), 2)))
        return res

    def compute_new_coordinate(self, interval):
        if interval > 0:
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
            elif float_range(self.x1, self.min_width, self.max_width, False) and float_range(self.y1, self.min_height, self.max_height, False):
                target_x, target_y = x, y
                x, y = self.set_in_limit(x, y)
                if x != target_x:
                    time_to_crash = abs((x-self.x1) * interval / (target_x - self.x1))
                    y = self.calculate_ordinate(self.y1, time_to_crash)
                elif y != target_y:
                    time_to_crash = abs((y-self.y1) * interval / (target_y - self.y1))
                    x = self.calculate_abscissa(self.x1, time_to_crash)
                x, y = self.set_in_limit(x, y)
                asyncio.Task(self.change_object(x, y, interval, time_to_crash))
            else:
                self.reset()
        self.controller.check_collision(self, interval)

    def move_to(self, x, y):
        logging.debug('Move %s to new coordinate - (%s, %s)' % (self.__class__.__name__, x, y))
        self.x, self.y = self.x1, self.y1
        self.x1, self.y1 = x, y
        self.response('update', frequency=STEP_INTERVAL)

    def set_angle(self, new_angle):
        if new_angle > MAX_ANGLE:
            new_angle -= MAX_ANGLE
        elif new_angle < 0:
            new_angle += MAX_ANGLE
        logging.info('Rotate %s from %s degree to %s degree' % (self.__class__.__name__, self.angle, new_angle))
        self.angle = new_angle
        self.compute_new_coordinate(ACTION_INTERVAL)

    def stop_unit(self):
        self.rotate_left_is_pressing = False
        self.rotate_right_is_pressing = False
        self.change_speed_up_is_pressing = False
        self.change_speed_down_is_pressing = False
        self.is_fire_active = False

    def set_speed(self, new_speed):
        self.speed = new_speed > 0 and new_speed or 0
        self.speed = MAX_SPEED if self.speed > MAX_SPEED else self.speed
        logging.info('Change %s speed to %s' % (self.__class__.__name__, self.speed))
        self.compute_new_coordinate(ACTION_INTERVAL)

    @asyncio.coroutine
    def notify_collision(self, other_unit, time_interval):
        yield from asyncio.sleep(time_interval)
        if not self.controller.units.get(self.id) or not self.controller.units.get(other_unit.id) or \
                not len(self.controller.collisions[self.id]) or not len(self.controller.collisions[other_unit.id]):
            return
        self.hit(other_unit)
        self.controller.cleanup_units([self, other_unit])

    def check_collision(self, other_unit, interval):
        # check if coordinate for two units is the same
        # for this check we also include width and height of unit's image
        # (other_unit.x - other_unit.width / 2 < self.x < other_unit.x + other_unit.width / 2)
        # (other_unit.y - other_unit.height / 2 < self.y < other_unit.y + other_unit.height / 2)
        # we don't need to check collision for Bullet with Bullet
        if not self.collision_check() and not other_unit.collision_check():
            return
        if id(self) != id(other_unit) and getattr(self, 'unit_id', '') != id(other_unit) and \
                getattr(other_unit, 'unit_id', '') != id(self):
            A = (self.x, self.y)
            B = (self.x1, self.y1)
            C = (other_unit.x, other_unit.y)
            D = (other_unit.x1, other_unit.y1)
            int_point = object_intersection((A, B), (C, D), round(self.width / 2), round(other_unit.width / 2))
            if int_point:
                A_B_distance = point_distance(A, B)
                A_P_distance = point_distance(A, int_point)
                C_D_distance = point_distance(C, D)
                C_P_distance = point_distance(C, int_point)
                if (A_B_distance - A_P_distance < 0 and A_B_distance > 0) or (C_D_distance - C_P_distance < 0 and C_D_distance > 0):
                    if ((B[0] + self.width / 2 > D[0] - other_unit.width / 2) and
                            (B[0] - self.width / 2 < D[0] + other_unit.width / 2) and
                            (B[1] + self.height / 2 > D[1] - other_unit.height / 2) and
                            (B[1] - self.height / 2 < D[1] + other_unit.height / 2)):
                        if A_B_distance > 0:
                            A_P_distance = A_B_distance
                        else:
                            C_P_distance = C_D_distance
                    else:
                        return
                if A_B_distance - A_P_distance >= 0 and A_B_distance > 0:
                    distance_to_unit = A_B_distance
                    distance_to_collision = A_P_distance
                else:
                    distance_to_unit = C_D_distance
                    distance_to_collision = C_P_distance
                time_to_point = distance_to_unit > 0 and round(interval * distance_to_collision / distance_to_unit, 2) or 0
                if time_to_point <= interval:
                    self.controller.collisions[self.id].append(other_unit.id)
                    self.controller.collisions[other_unit.id].append(self.id)
                    asyncio.Task(self.notify_collision(other_unit, time_to_point))

    def reset(self):
        raise NotImplementedError

    def hit(self, other_unit):
        raise NotImplementedError

    @asyncio.coroutine
    def change_object(self, x, y, interval, time_to_crash):
        raise NotImplementedError
    
    def collision_check(self):
        raise NotImplementedError

    def kill(self):
        logging.debug('Killing - %s ' % self.__class__.__name__)
        self.is_dead = True
        self.x1 = self.x
        self.stop_unit()
