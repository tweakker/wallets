from backend.apps.users.models import User
from backend.apps.wallets.models import Wallet


async def test_create_user_with_wallet(cli):
    """Testing create user with wallet."""
    url = cli.app.router['user-register'].url_for()
    payload = {
        'name': 'user',
        'password': '123',
    }
    resp = await cli.post(url, json=payload)
    assert resp.status == 200
    user = User.get(name=payload['name'])
    assert user
    wallet = Wallet.select().where(Wallet.user == user).first()
    assert wallet


async def test_user_name_unique(cli, user_factory):
    """Testing create user with not unique name."""
    url = cli.app.router['user-register'].url_for()
    payload = {
        'name': 'user',
        'password': '123',
    }
    # create user
    await user_factory(**payload)
    # trying to create with same name
    resp = await cli.post(url, json=payload)
    assert resp.status == 409
    # new user not created
    assert len(User.select()) == 1
