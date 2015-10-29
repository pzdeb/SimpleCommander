import asyncio
import json

from .generic.base import BaseView, StringBaseView, JSONBaseView, TemplateView
from .generic.routes import url_route
from src.simple_commander.controllers.main import GameController


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


@url_route('/api/hero/{hero_id:[a-z0-9-]+}/action/{action:[a-z_]+}/{direct:(stop)|(left)|(right)|(front)|(back)}')
class HeroAction(JSONBaseView):

    @asyncio.coroutine
    def post(self, request, hero_id=None, action=None, direct=None, *args, **kwargs):
        game = GameController(get_old=True)
        hero = game.units.get(hero_id, '')
        hero_action = getattr(hero, action, getattr(game, action, None))
        if hero and hero_action and callable(hero_action):
            if direct == 'stop':
                try:
                    game.ignore_heroes.remove(hero_id)
                except ValueError:
                    pass
            else:
                game.ignore_heroes.append(hero_id)
            parameter = hero if action == 'fire' else direct
            if action == 'rotate':
                hero.stop_rotate = direct
            elif action == 'change_speed':
                hero.stop_change_speed = direct
            asyncio.async(hero_action(parameter))
        else:
            return {'error': 'bad request'}


@url_route('/')
class StreamTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}

