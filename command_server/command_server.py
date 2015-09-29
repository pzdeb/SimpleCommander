import aiohttp_jinja2
import asyncio
import configparser
import logging
import jinja2
import websockets

import views

from aiohttp import server, web
from time import gmtime, strftime

from generic import routes


class BaseCommandServer(object):

    def __init__(self, server_type=None, host=None, port=None, loop=None):
        logging.info('Init %s Server on host %s:%s' % (server_type, host, port))
        self._server_type = server_type
        self._loop = loop or asyncio.get_event_loop()
        self._init_server(host, port)

    def start(self):
        self._server = self._loop.run_until_complete(self._server)
        logging.info(' %s has started.' % (self._server_type))

    def stop(self):
        self._server.close()
        logging.info('%s has stopped.' % (self._server_type))


class StreamCommandServer(BaseCommandServer):
    _instance = None

    def _init_server(self, host, port):
        self._app = web.Application(loop=self._loop)
        self._server = websockets.serve(self.process_request, host, port)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StreamCommandServer, cls).__new__(cls)
        return cls._instance

    @asyncio.coroutine
    def process_request(self, websocket, path):
        while True:
            yield from websocket.send(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            yield from asyncio.sleep(2)
        yield from websocket.close()


class HttpCommandServer(BaseCommandServer):
    _instance = None

    def _init_server(self, host, port):
        self._app = web.Application()
        self._load_routes()
        self._server = self._loop.create_server(self._app.make_handler(),
                                                host, port)

    def __init__(self, templates=None, **kwargs):
        super().__init__(**kwargs)
        if templates:
            aiohttp_jinja2.setup(self._app,
                                 loader=jinja2.FileSystemLoader(templates))
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HttpCommandServer, cls).__new__(cls)
        return cls._instance

    def _load_routes(self):
        logging.debug('Loading  Application Routes:\n%s' % '\n'.join(str(r) for r in routes.ROUTES))
        for route in routes.ROUTES:
            self._app.router.add_route(*route)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('etc/command_server.conf')
    host = config.get('commandServer', 'host')
    port = config.get('commandServer', 'port')
    templates = config.get('commandServer', 'templates')
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    server = HttpCommandServer(server_type='Http Server', host=host, port=port, loop=loop, templates=templates)
    socket_server = StreamCommandServer(server_type='Stream Server', host=host, port=8765, loop=loop)
    try:
        server.start()
        socket_server.start()
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        socket_server.stop()
        loop.close()
