import asyncio
import json

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
        data = yield from request.text()
        data = json.loads(data)
        value = data.get('value', '')
        if hero_action and action and value:
            if value == 'stop':
                hero.compute_new_coordinate(STEP_INTERVAL)
                try:
                    game.ignore_heroes.remove(hero.id)
                except ValueError:
                    pass
            elif action != 'fire':
                game.ignore_heroes.append(hero.id)
            hero_action(hero, value)
        else:
            return {'error': 'bad request'}

    @staticmethod
    def change_speed(hero, direct='stop'):
        if direct == 'stop':
            hero.stop_change_speed = True
        elif direct == 'up':
            hero.stop_change_speed = False
            asyncio.async(hero.change_speed(direct))
        elif direct == 'down':
            hero.stop_change_speed = False
            asyncio.async(hero.change_speed(direct))

    @staticmethod
    def fire(hero, status='stop'):
        if status == 'stop':
            hero.stop_fire = True
        elif status == 'start':
            hero.stop_fire = False
            asyncio.async(hero.fire())

    @staticmethod
    def rotate(hero, direct='stop'):
        if direct == 'stop':
            hero.stop_rotate = True
        elif direct == 'right':
            hero.stop_rotate = False
            asyncio.async(hero.rotate(direct))
        elif direct == 'left':
            hero.stop_rotate = False
            asyncio.async(hero.rotate(direct))


@url_route('/')
class StreamTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}

