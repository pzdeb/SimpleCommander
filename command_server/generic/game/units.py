import asyncio
from collections import namedtuple

Position2D = namedtuple('Position2D', ['x', 'y'])
Position3D = namedtuple('Position3D', ['x', 'y', 'z'])


class BaseUnit(object):
    name = 'Unit'
    speed_period = 300 #miliseconds needs to update state

    def __init__(self, game):
        self._game = game
        self._loop = game.loop or asyncio.get_event_loop()
        self._timer = self._loop.call_later(self.speed_period/1000, self.digest)

    def __hash__(self):
        return '{}-{}'.format(self.name, id(self))

    def digest(self):
        """
        Main method that will trigger periodically with own speed_period
        :return:
        """
        self._timer = self._loop.call_later(self.speed_period/1000, self.digest)

    def destroy(self):
        self._timer.cancel()

    def trigger(self, state):
        pass

class Positioned2DMixin(object):
    position = Position2D(x=0, y=0)


class Positioned3DMixin(object):
    position = Position3D(x=0, y=0)


class Unit2D(Positioned2DMixin, BaseUnit):
    pass


class Unit3D(Positioned3DMixin, BaseUnit):
    pass