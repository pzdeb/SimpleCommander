"""Base module for all units. """
import asyncio
# import logging
import math
import uuid
import time
from random import randint

from simple_commander.utils.float_range import float_range
from simple_commander.utils.constants import MAX_ANGLE, MAX_SPEED, STEP_INTERVAL, UNIT_PROPERTIES, UNITS, DEFAULT_SPEED, \
    DEFAULT_SPEED_BULLETS


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
        next_response = STEP_INTERVAL*1000 if tick_number * int(self.frequency*1000) == STEP_INTERVAL*1000 \
            else tick_number * int(self.frequency*1000) + int(self.frequency*1000)
        next_response = next_response/1000
        data = {action: self.to_dict()}
        data[action].update(kwargs)
        if not force:
            data[action].update({
                'frequency': next_response,
                'x1': self.calculate_abscissa(self.x, next_response),
                'y1': self.calculate_ordinate(self.y, next_response)
            })
        if not force:
            del data[action]['x']
            del data[action]['y']
        self.last_response = time.time()
        asyncio.async(self.controller.notify_clients(data))

    def to_dict(self, update=False):
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

    def move_to(self, x, y):
        self.x, self.y = self.x1, self.y1
        self.x1, self.y1 = x, y
        self.response('update', force=False)
        # logging.info('Move %s to new coordinate - (%s, %s)' % (self.__class__.__name__, x, y))

    def set_angle(self, new_angle):
        if new_angle > MAX_ANGLE:
            new_angle -= MAX_ANGLE
        elif new_angle < 0:
            new_angle += MAX_ANGLE
        # logging.info('Rotate %s from %s degree to %s degree' % (self.__class__.__name__, self.angle, new_angle))
        self.angle = new_angle
        self.compute_new_coordinate()
        self.response('update', force=True)

    def stop_unit(self):
        self.rotate_left_is_pressing = False
        self.rotate_right_is_pressing = False
        self.change_speed_up_is_pressing = False
        self.change_speed_down_is_pressing = False
        self.is_fire_active = False

    def set_speed(self, new_speed):
        self.speed = new_speed > 0 and new_speed or 0
        self.speed = MAX_SPEED if self.speed > MAX_SPEED else self.speed
        self.frequency = 1/(float(self.speed)/self.height) if self.speed else STEP_INTERVAL
        # logging.info('Change %s speed to %s' % (self.__class__.__name__, self.speed))
        self.compute_new_coordinate()
        self.response('update', force=True)

    def check_collision(self, other_unit):
        if (isinstance(self, Bullet) and (isinstance(other_unit, Bullet) or self.unit_id == id(other_unit))) or \
                (isinstance(other_unit, Bullet) and (isinstance(self, Bullet) or other_unit.unit_id == id(self))) or \
                (isinstance(self, Invader) and isinstance(other_unit, Invader)):
            return

        distance = math.sqrt(((self.x-other_unit.x)**2)+((self.y-other_unit.y)**2))
        if distance <= (self.width/2 + other_unit.width/2):
            self.hit(other_unit)

    def reset(self):
        raise NotImplementedError

    def hit(self, other_unit):
        raise NotImplementedError

    @asyncio.coroutine
    def change_object(self, x, y, time_to_crash):
        raise NotImplementedError

    def kill(self):
        # logging.info('Killing - %s ' % self.__class__.__name__)
        self.controller.remove_unit(self.id)


class Hero(Unit):

    def __init__(self, x, y, angle, hits=0, speed=0, life_count=5, frequency_fire=0.5, obj_type='',
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
            self.stop_unit()
            self.kill()
        self.response('update_life', force=True)

    def reset(self):
        self.speed = 0
        self.x = self.x1
        self.y = self.y1
        self.response('update', force=True)

    def hit(self, other_unit):
        # logging.info('In hit - %s and %s' % (self.__class__.__name__, other_unit.__class__.__name__))
        self.hits += 1
        self.decrease_life()
        if other_unit is Hero:
            other_unit.hits += 1
            other_unit.decrease_life()
        else:
            # Add hits if other_unit is Bullet
            if other_unit is Bullet:
                self.controller.add_hits(other_unit)
            other_unit.kill()

    @asyncio.coroutine
    def change_object(self, x, y, time_to_crash):
        """ Recalculate speed for Hero object. """
        self.speed = round(math.sqrt((x - self.x1) ** 2 + (y - self.y1) ** 2) / self.frequency)
        self.move_to(x, y)

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
        # logging.info('Reset %s angle. New angle - %s' % (self.__class__.__name__, self.angle))
        self.response('update', force=True)

    def hit(self, other_unit):
        # logging.info('In hit - %s and %s' % (self.__class__.__name__, other_unit. __class__.__name__))
        if isinstance(other_unit, Hero):
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
        if self.id in self.controller.units:
            self.move_to(x, y)
            self.reset()

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

    def hit(self, other_unit):
        # logging.info('In hit - %s(%s) and %s(%s)' % (self.__class__.__name__, self.unit_id, other_unit.__class__.__name__, other_unit.id))

        other_unit.bullet_kill(self)

    @asyncio.coroutine
    def change_object(self, x, y, time_to_crash):
        if self.id in self.controller.units:
            self.reset()