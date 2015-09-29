import asyncio

from generic.base import StringBaseView, JSONBaseView, TemplateView
from generic.routes import url_route


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

@url_route('/t')
class HelloTemplateView(TemplateView):
    template = 'index.html'

    @asyncio.coroutine
    def get(self, request):
        return {'name': 'World!!!'}