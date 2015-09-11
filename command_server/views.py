import asyncio

from generic.base import StringBaseView, JSONBaseView
from generic.routes import class_route


@class_route('/hello/{name:\w+}')
class HelloWorldView(StringBaseView):

    @asyncio.coroutine
    def get_string(self, request, name, *args, **kwargs):
        return u'Hello %s' % name


@class_route('/json')
class HelloWorldJsonView(JSONBaseView):

    @asyncio.coroutine
    def get_context_data(self, request, *args, **kwargs):
        return {'message': 'Hello! This is JSON'}