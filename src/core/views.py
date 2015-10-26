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


@url_route('/action')
class HeroAction(JSONBaseView):

    @asyncio.coroutine
    def post(self, request, *args, **kwargs):
        data = yield from request.text()
        data = json.loads(data)
        hero_id = data.get('id', '')
        action = data.get('action', '')
        value = data.get('value', 0)
        game = GameController(get_old=True)
        hero = game.units.get(hero_id, '')
        hero_action = getattr(hero, action, getattr(game, action, None))
        if hero and hero_action and callable(hero_action) and isinstance(value, int):
            parameter = hero if action == 'fire' else value
            hero_action(parameter)
            asyncio.async(game.run(loop=False))
        else:
            return {'error': 'bad request'}


@url_route('/')
class StreamTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}

