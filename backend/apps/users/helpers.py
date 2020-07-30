import hashlib
from aiohttp import web

from backend.settings import SECRET_KEY


def hashed_password(password: str) -> str:
    """Return hash from password."""
    salted = (password + SECRET_KEY).encode('UTF-8')
    return hashlib.sha256(salted).hexdigest()


def login_required(func):
    """Access for view only for auth users."""
    async def wrapped(self, *args, **kwargs):
        if self.request.user is None:
            raise web.HTTPForbidden()
        return await func(self, *args, **kwargs)
    return wrapped
