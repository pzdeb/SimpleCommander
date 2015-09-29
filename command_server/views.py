import asyncio
import aiohttp

from aiohttp import web
from generic.base import BaseView, StringBaseView, JSONBaseView
from generic.routes import url_route
from command_server import CommandServer


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


@url_route('/action/{action:\w+}')
class HeroAction(JSONBaseView):
    @asyncio.coroutine
    def get(self, request, action=None, *args, **kwargs):
        game = CommandServer.get_game_ctr()
        game_action = getattr(game, action, None)
        if game_action and callable(game_action):
            game_action()
            return{'message': 'Success'}

