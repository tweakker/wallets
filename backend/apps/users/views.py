import peewee
from aiohttp import web
from aiohttp_session import get_session
from aiohttp_validate import validate

from backend.db import database
from backend.logger import logger
from backend.apps.wallets.models import Wallet

from .helpers import hashed_password
from .models import User
from .schemas import USER_LOGIN_SCHEMA


@validate(request_schema=USER_LOGIN_SCHEMA)
async def register(data, request):
    """Create new user and wallet for him."""
    session = await get_session(request)
    if request.user:
        raise web.HTTPConflict()
    if User.exists(data['name']):
        raise web.HTTPConflict()
    with database.atomic() as transaction:
        try:
            new_user = await User.create_user(name=data['name'], password=data['password'])
            Wallet.create(user=new_user)
        except peewee.DatabaseError:
            transaction.rollback()
            logger.exception(f'Rollback from user registration: {data}')
            raise web.HTTPInternalServerError()
        else:
            session['user'] = new_user.id
    raise web.HTTPOk()


@validate(request_schema=USER_LOGIN_SCHEMA)
async def login(data, request):
    """Login view."""
    session = await get_session(request)
    if request.user:
        raise web.HTTPOk()
    try:
        user = User.get(
            name=data['name'],
            password=hashed_password(data['password'])
        )
    except User.DoesNotExist:
        raise web.HTTPUnauthorized()
    session['user'] = user.id
    raise web.HTTPOk()


async def logout(request: web.Request):
    """Logout view."""
    session = await get_session(request)
    session.invalidate()
    raise web.HTTPOk()
