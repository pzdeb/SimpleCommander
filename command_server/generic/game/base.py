import asyncio
from generic.game import REGISTERED_GAMES


class BaseGame(object):
    name = 'Game'
    version = '0.1.0'

    def __init__(self, loop):
        self.loop = loop or asyncio.get_event_loop()
        self.units = {}
        self._register_game()

    def __hash__(self):
        return '{} {}'.format(self.name, self.version)

    def _register_game(self):
        REGISTERED_GAMES[self] = self

    def add_unit(self, unit):
        self.units[unit] = unit

    def destroy_unit(self, unit):
        unit.destroy()
        del self.units[unit]