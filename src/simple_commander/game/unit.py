"""Base module for all units. """
import asyncio
import logging
import math
import uuid
import time
from random import randint

from simple_commander.utils.utils import float_range
from simple_commander.utils.constants import MAX_ANGLE, MAX_SPEED, STEP_INTERVAL, UNIT_PROPERTIES, UNITS, DEFAULT_SPEED, \
    DEFAULT_SPEED_BULLETS
from simple_commander.utils.line_intersection import object_intersection, point_distance


class Unit(object):
    """ Base class for all the units. """

    def __init__(self, x, y, angle, hits, speed, obj_type, bullet_type, dimension, controller=None):
        """ Basic initialization. """
        self.controller = controller
        self.type = obj_type
        self.bullet_filename = bullet_type
        self.last_calculation_time = time.time()
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
        self.frequency = 1/(float(self.speed)/self.height) if self.speed else STEP_INTERVAL
        self.rotate_is_pressing = False
        self.change_speed_is_pressing = False
        self.last_response = time.time()
        self.min_height = float(self.height / 2)
        self.min_width = float(self.width / 2)
        self.max_height = float(self.controller.game_field.get('height', 0) - self.height / 2)
        self.max_width = float(self.controller.game_field.get('width', 0) - self.width / 2)

    def response(self, action, force=False, **kwargs):
        if not self.controller or (not force and time.time() - self.last_response < STEP_INTERVAL):
            return
        tick_number = 1 // self.frequency
        next_response = STEP_INTERVAL if tick_number * self.frequency == STEP_INTERVAL \
            else tick_number * self.frequency + self.frequency
        data = {action: self.to_dict()}
        data[action].update(kwargs)
        if not force:
            data[action].update({
                'frequency': next_response,
                'x1': self.calculate_abscissa(self.x, next_response),
                'y1': self.calculate_ordinate(self.y, next_response)
            })
        self.last_response = time.time()
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
        res = point + self.speed * interval * math.sin(math.radians(180 - self.angle))
        return res

    def calculate_ordinate(self, point, interval):
        """ Calculate ordinate for point with interval. """
        res = point + self.speed * interval * math.cos(math.radians(180 - self.angle))
        return res

    def compute_new_coordinate(self):

        time_from_last_calculate = time.time() - self.last_calculation_time
        # Calculate real position
        if time_from_last_calculate < self.frequency:
            x = self.calculate_abscissa(self.x, time_from_last_calculate)
            y = self.calculate_ordinate(self.y, time_from_last_calculate)
            self.x1, self.y1 = self.set_in_limit(x, y)

        # Calculate future position
        x = self.calculate_abscissa(self.x1, self.frequency)
        y = self.calculate_ordinate(self.y1, self.frequency)

        self.last_calculation_time = time.time()
        if float_range(x, self.min_width, self.max_width) and float_range(y, self.min_height, self.max_height):
            self.move_to(x, y)
        elif float_range(self.x1, self.min_width, self.max_width, False) and float_range(self.y1, self.min_height, self.max_height, False):
            target_x, target_y = x, y
            x, y = self.set_in_limit(x, y)
            if x != target_x:
                time_to_crash = abs((x-self.x1) * self.frequency / (target_x - self.x1))
                y = self.calculate_ordinate(self.y1, time_to_crash)
            elif y != target_y:
                time_to_crash = abs((y-self.y1) * self.frequency / (target_y - self.y1))
                x = self.calculate_abscissa(self.x1, time_to_crash)
            x, y = self.set_in_limit(x, y)
            asyncio.async(self.change_object(x, y, time_to_crash))
        else:
            self.reset()
        # self.controller.check_collision(self)

    def move_to(self, x, y):
        logging.debug('Move %s to new coordinate - (%s, %s)' % (self.__class__.__name__, x, y))
        self.x, self.y = self.x1, self.y1
        self.x1, self.y1 = x, y
        self.response('update', force=False)

    def set_angle(self, new_angle):
        if new_angle > MAX_ANGLE:
            new_angle -= MAX_ANGLE
        elif new_angle < 0:
            new_angle += MAX_ANGLE
        logging.info('Rotate %s from %s degree to %s degree' % (self.__class__.__name__, self.angle, new_angle))
        self.angle = new_angle
        self.compute_new_coordinate()
        self.response('update', force=True)

    def stop_unit(self):
        self.rotate_left_is_pressing = False
        self.rotate_right_is_pressing = False
        self.change_speed_up_is_pressing = False
        self.change_speed_down_is_pressing = False
        self.fis_fire_active = False

    def set_speed(self, new_speed):
        self.speed = new_speed > 0 and new_speed or 0
        self.speed = MAX_SPEED if self.speed > MAX_SPEED else self.speed
        self.frequency = 1/(float(self.speed)/self.height) if self.speed else STEP_INTERVAL
        logging.info('Change %s speed to %s' % (self.__class__.__name__, self.speed))
        self.compute_new_coordinate()
        self.response('update', force=True)

    def notify_collision(self, other_unit):
        if isinstance(self, Bullet) and (isinstance(other_unit, Bullet) or self.unit_id == id(other_unit)):
            return
        self.hit(other_unit)
        self.controller.cleanup_units([self, other_unit])

    def check_collision(self, other_unit):
        # if (hasattr(self, 'unit_id') and id(self)) or (hasattr(other_unit, 'unit_id') and id(other_unit)):
        #     return
        # calculate first unit position
        time_from_last_calculate = time.time() - self.last_calculation_time
        first_unit_x = self.calculate_abscissa(self.x, time_from_last_calculate)
        first_unit_y = self.calculate_abscissa(self.y, time_from_last_calculate)

        # calculate second unit position
        if not other_unit.speed:
            second_unit_x = other_unit.x
            second_unit_y = other_unit.y
        else:
            time_from_last_calculate = time.time() - self.last_calculation_time
            second_unit_x = other_unit.calculate_abscissa(other_unit.x, time_from_last_calculate)
            second_unit_y = other_unit.calculate_abscissa(other_unit.y, time_from_last_calculate)

        distance = math.sqrt(((first_unit_x-second_unit_x)**2)+((first_unit_y-second_unit_y)**2))
        if distance <= (self.width/2 + other_unit.width/2):
            self.notify_collision(other_unit)

    # def check_collision(self, other_unit, interval):
    #     # check if coordinate for two units is the same
    #     # for this check we also include width and height of unit's image
    #     # (other_unit.x - other_unit.width / 2 < self.x < other_unit.x + other_unit.width / 2)
    #     # (other_unit.y - other_unit.height / 2 < self.y < other_unit.y + other_unit.height / 2)
    #     # we don't need to check collision for Bullet with Bullet
    #     if not self.collision_check() and not other_unit.collision_check():
    #         return
    #     if id(self) != id(other_unit) and getattr(self, 'unit_id', '') != id(other_unit) and \
    #             getattr(other_unit, 'unit_id', '') != id(self):
    #         A = (self.x, self.y)
    #         B = (self.x1, self.y1)
    #         C = (other_unit.x, other_unit.y)
    #         D = (other_unit.x1, other_unit.y1)
    #         int_point = object_intersection((A, B), (C, D), round(self.width / 2), round(other_unit.width / 2))
    #         if int_point:
    #             A_B_distance = point_distance(A, B)
    #             A_P_distance = point_distance(A, int_point)
    #             C_D_distance = point_distance(C, D)
    #             C_P_distance = point_distance(C, int_point)
    #             if (A_B_distance - A_P_distance < 0 and A_B_distance > 0) or (C_D_distance - C_P_distance < 0 and C_D_distance > 0):
    #                 if ((B[0] + self.width / 2 > D[0] - other_unit.width / 2) and
    #                         (B[0] - self.width / 2 < D[0] + other_unit.width / 2) and
    #                         (B[1] + self.height / 2 > D[1] - other_unit.height / 2) and
    #                         (B[1] - self.height / 2 < D[1] + other_unit.height / 2)):
    #                     if A_B_distance > 0:
    #                         A_P_distance = A_B_distance
    #                     else:
    #                         C_P_distance = C_D_distance
    #                 else:
    #                     return
    #             if A_B_distance - A_P_distance >= 0 and A_B_distance > 0:
    #                 distance_to_unit = A_B_distance
    #                 distance_to_collision = A_P_distance
    #             else:
    #                 distance_to_unit = C_D_distance
    #                 distance_to_collision = C_P_distance
    #             time_to_point = distance_to_unit > 0 and round(interval * distance_to_collision / distance_to_unit, 2) or 0
    #             if time_to_point <= interval:
    #                 self.controller.collisions[self.id].append(other_unit.id)
    #                 self.controller.collisions[other_unit.id].append(self.id)
    #                 asyncio.Task(self.notify_collision(other_unit, time_to_point))

    def reset(self):
        raise NotImplementedError

    def hit(self, other_unit):
        raise NotImplementedError

    @asyncio.coroutine
    def change_object(self, x, y, time_to_crash):
        raise NotImplementedError
    
    def collision_check(self):
        raise NotImplementedError

    def kill(self):
        logging.debug('Killing - %s ' % self.__class__.__name__)
        self.is_dead = True
        self.x1 = self.x


class Hero(Unit):

    def __init__(self, x, y, angle, hits=0, speed=0, life_count=3, frequency_fire=0.5, obj_type='',
                 bullet_type=UNITS.get('bullet_hero', {}).get('type', ''), dimension=0, controller=None):
        if not obj_type and len(UNITS.get('hero', [])):
            random_number = randint(0, len(UNITS.get('hero', [])) - 1)
            obj_type = UNITS.get('hero', [])[random_number].get('type', '')
            dimension = UNITS.get('hero', [])[random_number].get('dimension', '')
        super(Hero, self).__init__(x, y, angle, hits, speed, obj_type, bullet_type, dimension, controller=controller)
        self.frequency_fire = frequency_fire
        self.last_fire = time.time()
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
        self.response('update', force=True)

    def decrease_life(self):
        if self.life_count > 1:
            self.life_count -= 1
            self.response("delete", force=True)
            self.set_to_new_position()
            self.response("new", force=True)
        else:
            self.life_count = 0
            self.kill()
        self.response('update_life', force=True)

    def reset(self):
        self.speed = 0
        self.x = self.x1
        self.y = self.y1
        self.response('update', force=True)

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
    def change_object(self, x, y, time_to_crash):
        """ Recalculate speed for Hero object. """
        self.speed = round(math.sqrt((x - self.x1) ** 2 + (y - self.y1) ** 2) / self.frequency)
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
        self.compute_new_coordinate()
        logging.debug('Reset %s angle. New angle - %s' % (self.__class__.__name__, self.angle))
        self.response('update', force=True)

    def hit(self, other_unit):
        unit_class_name = other_unit. __class__.__name__
        logging.info('In hit - %s and %s' % (self.__class__.__name__, unit_class_name))
        if unit_class_name == 'Hero':
            other_unit.hits += 1
            other_unit.decrease_life()
            self.kill()
        elif isinstance(other_unit, Bullet):
            self.controller.add_hits(other_unit)
            other_unit.kill()
            self.kill()

    @asyncio.coroutine
    def change_object(self, x, y, time_to_crash):
        """ Reset Invader object. """
        asyncio.sleep(time_to_crash)
        self.move_to(x, y)
        self.reset()

    def collision_check(self):
        """ Do we need to check collision for Invader objects? """
        return True

    # def get_bullet_dimension(self):
    #     """ Get dimension for Invader object. """
    #     return UNITS.get('bullet_invader', {}).get('dimension', 0)

    def bullet_kill(self, obj_kill):
        """ Kill object after bullet hit. """
        obj_kill.controller.add_hits(obj_kill)
        self.kill()
        obj_kill.kill()


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

    @asyncio.coroutine
    def change_object(self, x, y, time_to_crash):
        pass

    def collision_check(self):
        """ Do we need to check collision for Bullet objects? """
        return False
