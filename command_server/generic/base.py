import asyncio
import json
import aiohttp


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

    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        result = yield from self.get_string(request, *args, **kwargs)
        result = bytes(result, 'utf8')
        response = aiohttp.Response(
            request.transport, 200, http_version=request.version
        )
        response.add_header('Content-Type', 'text/html')
        response.send_headers()
        response.write(result)
        yield from response.write_eof()


class ContextResponseMixin(object):

    def get_context_data(self, request, *args, **kwargs):
        raise NotImplementedError


class JSONBaseView(ContextResponseMixin, StringBaseView):

    @asyncio.coroutine
    def get_string(self, request, *args, **kwargs):
        result = yield from self.get_context_data(request, *args, **kwargs)
        return json.dumps(result)