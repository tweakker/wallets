import asyncio
import pytest
from unittest import mock
from decimal import Decimal

from backend.apps.wallets.exceptions import *
from backend.apps.wallets.models import Transaction

from backend.tests.helpers import user_auth


class TestTopUp:
    """Testing top up wallet."""

    @pytest.fixture(autouse=True)
    def _init(self, app, cli):
        self.url = app.router['wallet-top-up'].url_for()
        self.cli = cli

    @pytest.fixture
    async def wallet(self, cli, user_factory, wallet_factory):
        """Create user, wallet and auth cli with user credentials."""
        user = await user_factory(name='user', password='123')
        wallet = await wallet_factory(user=user)
        await user_auth(cli, 'user', '123')
        return wallet

    async def top_up_wallet(self, data):
        resp = await self.cli.post(self.url, json=data)
        return resp

    async def test_top_up_wallet(self, wallet):
        """Testing top up wallet."""
        assert wallet.balance == 0
        resp = await self.top_up_wallet({
            'value': '10.21',
            'currency': 'USD',
        })
        assert resp.status == 200
        wallet = wallet.refresh()
        assert wallet.balance == Decimal('10.21')

    async def test_cant_top_up_wallet_if_currency_wrong(self, wallet):
        """Testing top up wallet."""
        assert wallet.balance == 0
        resp = await self.top_up_wallet({
            'value': '10.21',
            'currency': 'RUB',
        })
        assert resp.status == 400
        wallet = wallet.refresh()
        assert wallet.balance == 0

    async def test_double_request_top_up_only_once(self, wallet):
        """Test if user send identical requests several times only one has performed."""
        assert wallet.balance == 0
        payload = {
            'value': '1',
            'currency': 'USD',
        }
        value = Decimal(payload['value'])
        resp_1 = await self.top_up_wallet(payload)
        resp_2 = await self.top_up_wallet(payload)
        assert resp_1.status == resp_2.status == 200
        wallet = wallet.refresh()
        # only one transaction was create
        assert len(Transaction.select().where(
            Transaction.trx_from == None,
            Transaction.trx_to == wallet,
            Transaction.value == value,
        )) == 1
        # balance changed only once
        assert wallet.balance == value


class TestTransfers:
    """Testing transfers between wallets."""

    @pytest.fixture(autouse=True)
    def _init(self, app, cli):
        self.url = app.router['wallet-transfer'].url_for()
        self.cli = cli

    @pytest.fixture
    async def wallet_from(self, cli, user_factory, wallet_factory):
        """Create user, wallet and auth cli with user credentials."""
        user = await user_factory(name='user', password='123')
        wallet = await wallet_factory(user=user, balance=Decimal('11.21'))
        await user_auth(cli, 'user', '123')
        return wallet

    @pytest.fixture
    async def wallet_to(self, user_factory, wallet_factory):
        """Create user, wallet and auth cli with user credentials."""
        user = await user_factory(name='user2', password='123')
        wallet = await wallet_factory(user=user)
        return wallet

    async def send_money(self, data):
        data['currency'] = data.get('currency', 'USD')
        resp = await self.cli.post(self.url, json=data)
        return resp

    async def test_transfer_between_two_wallets(self, wallet_from, wallet_to):
        """Test one user can send money to other."""
        payload = {
            'to_name': wallet_to.user.name,
            'value': '10.21',
            'currency': 'USD',
        }
        value = Decimal(payload['value'])
        old_balance_from, old_balance_to = wallet_from.balance, wallet_to.balance
        resp = await self.send_money(payload)
        assert resp.status == 200
        # balances changed
        wallet_from = wallet_from.refresh()
        assert wallet_from.balance == old_balance_from - value
        wallet_to = wallet_to.refresh()
        assert wallet_to.balance == old_balance_to + value
        # transaction created
        try:
            Transaction.get(trx_from=wallet_from, trx_to=wallet_to)
        except Transaction.DoesNotExist:
            pytest.fail("Unexpected Transaction.DoesNotExist")

    async def test_cant_send_money_if_balance_low(self, wallet_from, wallet_to):
        """Test user cant send money if balance is too low."""
        wallet_from.balance = 0
        wallet_from.save()
        resp = await self.send_money({
            'to_name': wallet_to.user.name,
            'value': '1',
        })
        assert resp.status == 400

    async def test_cant_send_money_with_different_currency(self, wallet_from, wallet_to):
        """Test cant send money with different currency then recipient have."""
        wallet_from.currency = 'RUB'
        wallet_from.save()
        resp = await self.send_money({
            'to_name': wallet_to.user.name,
            'value': '1',
            'currency': 'RUB',
        })
        assert resp.status == 400

    async def test_double_requests_create_only_one_transfer(self, wallet_from, wallet_to):
        """Test if user send identical requests several times only one has performed."""
        payload = {
            'to_name': wallet_to.user.name,
            'value': '1',
        }
        value = Decimal(payload['value'])
        # send one request 2 times
        resp_1 = await self.send_money(payload)
        resp_2 = await self.send_money(payload)
        assert resp_1.status == resp_2.status == 200
        # only one transaction was create
        assert len(Transaction.select().where(
            Transaction.trx_from == wallet_from,
            Transaction.trx_to == wallet_to,
            Transaction.value == value,
        )) == 1
        old_balance_from, old_balance_to = wallet_from.balance, wallet_to.balance
        wallet_from, wallet_to = wallet_from.refresh(), wallet_to.refresh()
        # balances changed like only one request was
        assert wallet_from.balance == old_balance_from - value
        assert wallet_to.balance == old_balance_to + value

    async def test_parallel_transaction_rollback(self, wallet_from, wallet_to, wallet_factory):
        """Test if one of async transactions make balance lower than 0 it finished and rollback."""
        wallet_from.balance = 5
        wallet_from.save()
        assert wallet_to.balance == 0
        wallet_to_2 = await wallet_factory()
        assert wallet_to_2.balance == 0
        # make two async requests
        request_1 = self.send_money({
            'to_name': wallet_to.user.name,
            'value': '5',
        })
        request_2 = self.send_money({
            'to_name': wallet_to_2.user.name,
            'value': '5',
        })
        # mock prevalidation
        with mock.patch('backend.apps.wallets.models.Wallet._transfer_prevalidate'):
            # run both requests async
            resp_1, resp_2 = await asyncio.gather(request_1, request_2)
        # first request completed
        assert resp_1.status == 200
        # next return 400 and message about low balance
        assert resp_2.status == 400
        assert await resp_2.text() == BalanceTooLow.text
        # wallet_from balance not lower then 0
        wallet_from = wallet_from.refresh()
        assert wallet_from.balance == 0
        # first wallet balance updated
        wallet_to = wallet_to.refresh()
        assert wallet_to.balance == 5
        # second wallet balance not changed
        wallet_to_2 = wallet_to_2.refresh()
        assert wallet_to_2.balance == 0

