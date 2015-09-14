import asyncio
from collections import namedtuple

Position = namedtuple('Position', ['x', 'y'])


class BaseUnit(object):
    name = 'Unit'
    position = Position(x=0, y=0)
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