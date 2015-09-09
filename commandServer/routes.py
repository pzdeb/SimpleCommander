import asyncio
from aiohttp import web

#Test View
@asyncio.coroutine
def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(body=text.encode('utf-8'))

ROUTES = (
	(r'/{name}', handle),
)
