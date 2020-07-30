import peewee
from backend.db import BaseModel

from .helpers import hashed_password


class User(BaseModel):
    """Class for users table."""

    name = peewee.CharField(max_length=32, unique=True)
    password = peewee.CharField(max_length=128)

    @classmethod
    def exists(cls, name: str) -> bool:
        """Return True if user with name already exists."""
        exists = cls.select().where(cls.name == name)
        return bool(exists)

    @classmethod
    async def create_user(cls, *args, **kwargs) -> 'User':
        """Async create user object."""
        kwargs["password"] = hashed_password(kwargs["password"])
        obj = cls.create(*args, **kwargs)
        return obj
