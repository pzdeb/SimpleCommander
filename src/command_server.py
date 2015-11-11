import asyncio
import configparser
import json
import logging
import os

import aiohttp_jinja2
import jinja2
from aiohttp import server, web, MsgType

from core import routes, views
from simple_commander.main import get_game, STEP_INTERVAL


class HttpCommandServer(object):
    _instance = None

    def __init__(self,  host=None, port=None, templates=None, **kwargs):
        logging.info('Init Server on host %s:%s' % (host, port))
        self._loop = asyncio.get_event_loop()
        self._ws = web.WebSocketResponse()
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

        while ws.started:
            msg = yield from ws.receive()
            if msg.tp == MsgType.text:
                if msg.data == 'close':
                    yield from ws.close()
                    self._controller.del_web_socket(ws)
                    if self._controller.units.get(my_hero.id):
                        self._controller.remove_unit(my_hero.id)
                else:
                    data = json.loads(msg.data)
                    if 'start' in data:
                        self._controller.websockets.append(ws)
                        asyncio.async(self._controller.run())
                        my_hero = self._controller.new_hero()
                        my_hero.set_name(data['start'])
                        start_conditions = {'init': {
                            'hero_id': my_hero.id,
                            'game': self._controller.game_field,
                            'units': self._controller.get_units(),
                            'frequency': STEP_INTERVAL}}
                        ws.send_str(json.dumps(start_conditions))
                    else:
                        for key in data:
                            action = getattr(my_hero, key, '')
                            if key.startswith('stop'):
                                my_hero.compute_new_coordinate(STEP_INTERVAL)
                                try:
                                    self._controller.ignore_heroes.remove(my_hero.id)
                                except ValueError:
                                    pass
                            elif not key.endswith('fire') and key != 'set_name':
                                self._controller.ignore_heroes.append(my_hero.id)
                            if data[key]:
                                action(data[key])
                            else:
                                action(my_hero)
            elif msg.tp == MsgType.close:
                logging.info('websocket connection closed')
                self._controller.del_web_socket(ws)
                if self._controller.units.get(my_hero.id):
                        self._controller.remove_unit(my_hero.id)
            elif msg.tp == MsgType.error:
                logging.info('ws connection closed with exception %s', ws.exception())
                self._controller.del_web_socket(ws)
                if self._controller.units.get(my_hero.id):
                        self._controller.remove_unit(my_hero.id)

        yield from ws.close()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('etc/command_server.conf')
    host = config.get('commandServer', 'host')
    port = os.environ.get('PORT', config.get('commandServer', 'port'))
    static_path = config.get('commandServer', 'static_path')
    templates = config.get('commandServer', 'templates')
    logging.basicConfig(level=logging.DEBUG)
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