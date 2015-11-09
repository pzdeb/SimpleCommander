import asyncio
import re

from core.base import StringBaseView, JSONBaseView, TemplateView
from .routes import url_route
from simple_commander.main import get_game, STEP_INTERVAL


@url_route('/hello/{name:\w+}')
class HelloWorldView(StringBaseView):

    @asyncio.coroutine
    def get(self, request, name=None, *args, **kwargs):
        return u'Hello %s' % name


@url_route('/json')
class HelloWorldJsonView(JSONBaseView):

    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        return {'message': 'Hello! This is JSON'}


@url_route('/api/hero/{hero_id:[a-z0-9-]+}/action/{action:[a-z_]+}')
class HeroAction(JSONBaseView):

    @asyncio.coroutine
    def post(self, request, hero_id=None, action=None, *args, **kwargs):
        game = get_game()
        hero = game.units.get(hero_id, '')
        hero_action = getattr(self, action, None)
        if hero_action and action:
            if re.match('^stop', action):
                hero.compute_new_coordinate(STEP_INTERVAL)
                try:
                    game.ignore_heroes.remove(hero.id)
                except ValueError:
                    pass
            elif not re.match('fire', action):
                game.ignore_heroes.append(hero.id)
            hero_action(hero)
        else:
            return {'error': 'bad request'}

    @staticmethod
    def change_speed_up(hero):
        hero.change_speed_is_pressing = True
        asyncio.async(hero.change_speed('up'))

    @staticmethod
    def change_speed_down(hero):
        hero.change_speed_is_pressing = True
        asyncio.async(hero.change_speed('down'))

    @staticmethod
    def stop_change_speed(hero):
        hero.change_speed_is_pressing = False

    @staticmethod
    def start_fire(hero):
        hero.fire_is_pressing = True
        asyncio.async(hero.fire())

    @staticmethod
    def stop_fire(hero):
        hero.fire_is_pressing = False

    @staticmethod
    def rotate_right(hero):
        hero.rotate_is_pressing = True
        asyncio.async(hero.rotate('right'))

    @staticmethod
    def rotate_left(hero):
        hero.rotate_is_pressing = True
        asyncio.async(hero.rotate('left'))

    @staticmethod
    def stop_rotate(hero):
        hero.rotate_is_pressing = False


@url_route('/')
class StreamTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}

