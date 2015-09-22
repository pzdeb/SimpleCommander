import asyncio
from aiohttp.web_urldispatcher import UrlDispatcher
from functools import wraps
from generic.base import BaseView

ROUTES = []


def dispatch(view, method):
    @wraps(method)
    @asyncio.coroutine
    def _dispatch(request, *args, **kwargs):
        kwargs.update(request.match_info)
        request.exec_method = method
        return view.dispatch(request, *args, **kwargs)
    return _dispatch


def route(path_reg, method='*'):
    """
    Route decorator for simple handlers

    :param path_reg: string
    :param method: string
    :return:
    """
    def _dec(func): # maybe it should be as coroutine?
        ROUTES.append((method, path_reg, func))

        def _run(*args, **kwargs):
            return func(*args, **kwargs)
        return _run
    return _dec


def url_route(path_reg):
    """
    Route decorator for class-based views

    :param path_reg: string
    :return:
    """
    def handler_builder(cls):
        assert issubclass(cls, BaseView), 'Class {!r} should inherit BaseView'.format(cls)
        view = cls.as_view()
        for method in UrlDispatcher.METHODS:
            method_l = method.lower()
            method_handler = getattr(view, method_l, None)
            if callable(method_handler):
                setattr(view, method_l, route(path_reg, method)(dispatch(view, method_handler)))
        return cls
    return handler_builder
