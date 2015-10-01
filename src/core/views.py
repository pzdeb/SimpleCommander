import asyncio

from .generic.base import BaseView, StringBaseView, JSONBaseView, TemplateView
from .generic.routes import url_route
from src.command_server.command_server import CommandServer


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

        return {'message': 'Hello! This is JSON'}

@url_route('/')
class StreamTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}

