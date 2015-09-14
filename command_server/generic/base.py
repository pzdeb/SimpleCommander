import asyncio
import json

from aiohttp.web_reqrep import Response


class BaseView(object):

    @classmethod
    def as_view(cls):
        view = cls()
        return view

    @asyncio.coroutine
    def dispatch(self, request, method, *args, **kwargs):
        yield from method(request, *args, **kwargs)

    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        raise NotImplementedError

    @asyncio.coroutine
    def post(self, request, *args, **kwargs):
        raise NotImplementedError

    @asyncio.coroutine
    def put(self, request, *args, **kwargs):
        raise NotImplementedError

    @asyncio.coroutine
    def delete(self, request, *args, **kwargs):
        raise NotImplementedError


class StringResponseMixin(object):

    def get_string(self, request, *args, **kwargs):
        raise NotImplementedError


class StringBaseView(StringResponseMixin, BaseView):
    content_type = 'text/html'

    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        result = yield from self.get_string(request, *args, **kwargs)
        result = bytes(result, 'utf8')
        response = Response(
            body=result,
            status=200,
            content_type=self.content_type
        )
        return response


class ContextResponseMixin(object):

    def get_context_data(self, request, *args, **kwargs):
        raise NotImplementedError


class JSONBaseView(ContextResponseMixin, StringBaseView):

    @asyncio.coroutine
    def get_string(self, request, *args, **kwargs):
        result = yield from self.get_context_data(request, *args, **kwargs)
        return json.dumps(result)