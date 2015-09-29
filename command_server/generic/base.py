import asyncio
import aiohttp
import aiohttp_jinja2
import json

from aiohttp import web
from aiohttp.web_reqrep import Response


class BaseView(object):

    @classmethod
    def as_view(cls):
        view = cls()
        return view

    @asyncio.coroutine
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = yield from request.exec_method(request, *args, **kwargs)
        return self.finalize_response(response)

    def finalize_response(self, response):
        return response


class StringResponseMixin(object):
    content_type = 'text/html'

    def finalize_response(self, response):
        response = Response(
            body= bytes(response, 'utf8'),
            content_type=self.content_type
        )
        return response


class StringBaseView(StringResponseMixin, BaseView):
    pass


class ContextResponseMixin(StringResponseMixin):
    content_type = 'application/json'

    def finalize_response(self, response):
        response = json.dumps(response)
        response = super().finalize_response(response)
        return response


class JSONBaseView(ContextResponseMixin, StringBaseView):
    pass


class TemplateResponseMixin(object):
    template = None

    def finalize_response(self, response):
        """
        So basically it will block event loop, such as it use blocking IO with files.
        Maybe make sense to use threading for template loading.
        """
        return aiohttp_jinja2.render_template(self.template, self.request, response)


class TemplateView(TemplateResponseMixin, BaseView):
    pass


class RedirectView(BaseView):
    redirect_url = None

    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        return

    def finalize_response(self, response):
        return aiohttp.web.HTTPFound(response or self.redirect_url)


class WebSocketView(BaseView):

    @asyncio.coroutine
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.ws = web.WebSocketResponse()
        self.ws.start(request)
        while True:
            msg = yield from self.ws.receive()
            self.on_message(msg)

    def on_message(self, msg):
        pass

    def send(self, msg):
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        self.ws.send_str(msg)

    def get(self):
        pass