import random
import string

import pytest

from backend import settings
from backend.app import create_app
from backend.apps.users.models import User
from backend.apps.wallets.models import Wallet
from backend.apps.wallets.enums import USD
from backend.db_init import db_init, db_clear


@pytest.fixture
async def app(monkeypatch):
    monkeypatch.setattr(settings, 'DB_NAME', settings.TEST_DATABASE_NAME)
    return create_app()


@pytest.fixture
async def cli(app, aiohttp_client):
    return await aiohttp_client(app)


@pytest.fixture(autouse=True)
async def db_initialize(app):
    db_clear(app)
    db_init(app)
    yield


@pytest.fixture
def user_factory():
    """Creates user."""

    def pswd_generator():
        return str(random.randint(100, 999))

    def name_generator():
        return ''.join(random.choice(string.ascii_lowercase) for i in range(5)).capitalize()

    async def factory(**kwargs) -> User:
        kwargs['name'] = kwargs.get('name', name_generator())
        kwargs['password'] = kwargs.get('password', pswd_generator())
        return await User.create_user(**kwargs)

    return factory


@pytest.fixture
def wallet_factory(user_factory):
    """Create wallet."""
    async def factory(**kwargs) -> Wallet:
        kwargs['user'] = kwargs.get('user', await user_factory())
        kwargs['currency'] = kwargs.get('currency', USD)
        return Wallet.create(**kwargs)
    return factory
