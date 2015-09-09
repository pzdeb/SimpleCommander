import asyncio
import aiohttp
import configparser
import logging

from aiohttp import web
from routes import ROUTES

class CommandServer(object):
    _instance = None

    def __init__(self, host=None, port=None, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self.app = web.Application(loop=loop)()
        self._load_routes()
        self._server = self._loop.create_server(self.app.make_handler(), host, port)
        logging.info('Init Server on host %s:%s' %(host, port))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandServer, cls).__new__(cls)
        return cls._instance

    def start(self, and_loop=True):
        self._server = self._loop.run_until_complete(self._server)
        logging.info('Conection')
        if and_loop:
            self._loop.run_forever()

    def stop(self, and_loop=True):
        self._server.close()
        if and_loop:
            self._loop.close()
        logging.info('server has stopped')

    def _load_routes(self):
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