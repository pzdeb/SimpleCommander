import aiohttp
import aiohttp_jinja2
import asyncio
import configparser
import logging
import views
import websockets

import views

from aiohttp import server, web
from time import gmtime, strftime

from generic import routes
from controllers.main import GameController


class CommandServer(object):

    _instance = None
    _controller = None

    def __init__(self,  host=None, port=None, templates=None, **kwargs):
        logging.info('Init Server on host %s:%s' % (host, port))
        super().__init__(**kwargs)
        if templates:
            aiohttp_jinja2.setup(self._app,
                                 loader=jinja2.FileSystemLoader(templates))
        self._loop = asyncio.get_event_loop()
        self._ws = web.WebSocketResponse()
        self._app = web.Application(loop=self._loop)
        asyncio.async(self.get_game_ctr().run())

        self._load_routes()
        self._server = self._loop.create_server(self._app.make_handler(),
                                                host, port)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandServer, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_game_ctr(cls):
        if not cls._controller:
            cls._controller = GameController(50, 50, 2)
        return cls._controller

    def start(self):
        self._server = self._loop.run_until_complete(self._server)
        logging.info('Server has started.')
        self._loop.run_forever()

    def stop(self):
        self._server.close()
        logging.info('Server has stopped.')

    def _load_routes(self):
        logging.debug('Loading  Application Routes:\n%s' % '\n'.join(str(r) for r in routes.ROUTES))
        self._app.router.add_route('GET', '/ws_stream', self.ws_stream)
        for route in routes.ROUTES:
            self._app.router.add_route(*route)

    @asyncio.coroutine
    def ws_stream(self, request, *args, **kwargs):
        self._ws.start(request)
        while True:
            msg = yield from self._ws.receive()

            if msg.tp == aiohttp.MsgType.text:
                if msg.data == 'close':
                    yield from self._ws.close()
                else:
                    self._ws.send_str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                    yield from asyncio.sleep(2)
            elif msg.tp == aiohttp.MsgType.close:
                logging.info('websocket connection closed')
            elif msg.tp == aiohttp.MsgType.error:
                logging.info('ws connection closed with exception %s',
                    self._ws.exception())
        yield from self._ws.close()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('etc/command_server.conf')
    host = config.get('commandServer', 'host')
    port = config.get('commandServer', 'port')
    templates = config.get('commandServer', 'templates')
    logging.basicConfig(level=logging.DEBUG)
    server = CommandServer(host=host, port=port, templates=templates)
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
