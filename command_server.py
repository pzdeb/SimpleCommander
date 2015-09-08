import asyncio
import aiohttp
import logging

from aiohttp import web

#Test View
@asyncio.coroutine
def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(body=text.encode('utf-8'))

class CommandServer(object):
    _instance = None

    def __init__(self, host=None, port=None, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self.app = web.Application(loop=loop)
        self.app.router.add_route('GET', '/{name}', handle)
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    server = CommandServer('0.0.0.0', 8000)

    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()