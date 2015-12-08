import asyncio
import configparser
import json
import logging
import os

import aiohttp_jinja2
import jinja2
from aiohttp import server, web, MsgType

from core import routes, views
from simple_commander.game.init_game import get_game
from simple_commander.utils.constants import STEP_INTERVAL 

class HttpCommandServer(object):
    _instance = None

    def __init__(self,  host=None, port=None, templates=None, **kwargs):
        logging.info('Init Server on host %s:%s' % (host, port))
        self._loop = asyncio.get_event_loop()
        self._app = web.Application(loop=self._loop)

        self._load_routes()
        self._load_static()
        self._controller = get_game(600, 800, 5)
        self._server = self._loop.create_server(self._app.make_handler(),
                                                host, port)

        if templates:
            aiohttp_jinja2.setup(self._app,
                                 loader=jinja2.FileSystemLoader(templates))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HttpCommandServer, cls).__new__(cls)
        return cls._instance

    def start(self):
        self._server = self._loop.run_until_complete(self._server)
        logging.info('Server has started.')

    def stop(self):
        self._server.close()
        logging.info('Server has stopped.')

    def _load_routes(self):
        logging.debug('Loading  Application Routes:\n%s' % '\n'.join(str(r) for r in routes.ROUTES))
        self._app.router.add_route('GET', '/ws_stream', self.ws_stream)
        for route in routes.ROUTES:
            self._app.router.add_route(*route)

    def _load_static(self):
        self._app.router.add_static('/static', static_path)

    @asyncio.coroutine
    def ws_stream(self, request, *args, **kwargs):
        ws = web.WebSocketResponse()
        ws.start(request)
        while not ws.closed:
            msg = yield from ws.receive()
            if msg.tp == MsgType.text:
                if msg.data == 'close':
                    yield from ws.close()
                    self._controller.drop_connection(ws)
                else:
                    data = json.loads(msg.data)
                    if 'start' in data:
                        self._controller.start(ws, data['start'])
                    else:
                        self._controller.do_action(data)
            elif msg.tp == MsgType.close:
                logging.info('websocket connection closed')
                self._controller.drop_connection(ws)
            elif msg.tp == MsgType.error:
                logging.info('ws connection closed with exception %s', ws.exception())
                self._controller.drop_connection(ws)

        return ws


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('etc/command_server.conf')
    host = config.get('commandServer', 'host')
    port = os.environ.get('PORT', config.get('commandServer', 'port'))
    static_path = config.get('commandServer', 'static_path')
    templates = config.get('commandServer', 'templates')
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    server = HttpCommandServer(host=host, port=port, templates=templates)
    try:
        server.start()
        loop.run_forever()

    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()
