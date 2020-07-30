from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp import web

from .urls import routes
from .middlewares import request_user_middleware
from .db import database
from . import settings


def create_app() -> web.Application:
    """Create app object."""

    middlewares = [
        session_middleware(SimpleCookieStorage()),  # unsafe
        request_user_middleware,
    ]

    _app = web.Application(middlewares=middlewares)

    # add routes
    for route in routes:
        _app.router.add_route(**route)

    return _app


app = create_app()
