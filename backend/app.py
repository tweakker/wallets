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

    database.init(
        settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
    )

    _app.db = database

    # add routes
    for route in routes:
        _app.router.add_route(**route)

    return _app


app = create_app()
