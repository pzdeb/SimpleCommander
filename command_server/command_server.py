import asyncio
import aiohttp
import configparser
import logging

from aiohttp import server
from aiohttp.multidict import MultiDict
from routes import ROUTES
from urllib.parse import urlparse, parse_qsl


class HttpRequestHandler(aiohttp.server.ServerHttpProtocol):
    @asyncio.coroutine
    def handle_request(self, request, payload=None):
        response = aiohttp.Response(
            self.writer, 200, http_version=request.version
        )
        response.add_header('Content-Type', 'application/json')

        handler = ROUTES.get(request.path)
        if not handler:
            logging.error('Method not found for: %s' % request.path)
            raise aiohttp.errors.HttpBadRequest('Bad Request')

        method = getattr(handler(), request.method.lower(), None)
        request_params = MultiDict(parse_qsl(urlparse(request.path).query))
        method_response = method(request, request_params)
        response.send_headers()
        response.write(method_response)
        yield from response.write_eof()


class CommandServer(object):
    _instance = None

    def __init__(self, host=None, port=None, loop=None):
        logging.info('Init Server on host %s:%s' % (host, port))
        self._loop = loop or asyncio.get_event_loop()
        self._server = self._loop.create_server(lambda: HttpRequestHandler(debug=True, keep_alive=75),
                                                host, port)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandServer, cls).__new__(cls)
        return cls._instance

    def start(self, and_loop=True):
        self._server = self._loop.run_until_complete(self._server)
        logging.info('Listening established on {0}'.format(
            self._server.sockets[0].getsockname()))
        if and_loop:
            self._loop.run_forever()

    def stop(self, and_loop=True):
        logging.info('Server has stopped on {0}'.format(
            self._server.sockets[0].getsockname()))
        self._server.close()
        if and_loop:
            self._loop.close()

    def _load_routes(self):
        logging.debug('Loading  Application Routes %s' % ROUTES)
        for url, callback in ROUTES:
            self.app.router.add_route('GET', url, callback)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('etc/command_server.conf')
    host = config.get('commandServer', 'host')
    port = config.get('commandServer', 'port')
    logging.basicConfig(level=logging.DEBUG)
    server = CommandServer(host, port)

    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
