import aiohttp
import aiohttp_jinja2
import asyncio
import configparser
import logging
import jinja2
import views

from aiohttp import server, web
from generic import routes


class CommandServer(object):
    _instance = None

    def __init__(self, host=None, port=None, templates=None, loop=None):
        logging.info('Init Server on host %s:%s' % (host, port))
        self._loop = loop or asyncio.get_event_loop()
        #TODO: MOve debug mode to config file.
        self._app = web.Application(loop=loop)
        if templates:
            aiohttp_jinja2.setup(self._app,
                                 loader=jinja2.FileSystemLoader(templates))
        self._load_routes()
        self._server = self._loop.create_server(self._app.make_handler(),
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
    server = CommandServer(host, port, templates)

    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
