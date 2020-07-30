from aiohttp import web
from aiohttp_session import get_session

from backend.apps.users.models import User


@web.middleware
async def request_user_middleware(request, handler):
    """Add user object to request."""
    session = await get_session(request)
    request.user = None
    try:
        user = User.get(id=session['user'])
    except (User.DoesNotExist, KeyError):
        pass
    else:
        request.user = user
    resp = await handler(request)
    return resp
