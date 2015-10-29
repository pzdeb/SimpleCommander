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


@url_route('/api/hero/{hero_id:[a-z0-9-]+}/action/{action:[a-z_]+}/{run:[0-2]+}')
class HeroAction(JSONBaseView):

    @asyncio.coroutine
    def post(self, request, hero_id=None, action=None, run=None, *args, **kwargs):
        game = GameController(get_old=True)
        hero = game.units.get(hero_id, '')
        hero_action = getattr(hero, action, getattr(game, action, None))
        if hero and hero_action and callable(hero_action):
            run = int(run)
            parameter = hero if action == 'fire' else run
            game.stop = True
            if action == 'rotate':
                hero.rotation = run
            elif action == 'change_speed':
                hero.direction = run
            asyncio.async(hero_action(parameter))
            game.stop = False
            asyncio.async(game.run())
        else:
            return {'error': 'bad request'}


@url_route('/')
class StreamTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}

