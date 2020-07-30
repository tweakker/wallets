import datetime
import typing as t
from decimal import Decimal, InvalidOperation

from aiohttp import web
from aiohttp_validate import validate

from backend.logger import logger
from backend.types import JSON
from backend.settings import DOUBLE_TRANSACTION_CHECK_TIMEOUT
from backend.apps.users.helpers import login_required
from backend.apps.users.models import User
from backend.apps.wallets.enums import CURRENCIES
from backend.apps.wallets.models import Wallet, Transaction

from .exceptions import *
from .schemas import TRANSFER_SCHEMA, WALLET_TOP_UP_SCHEMA


class BaseWalletView(web.View):
    """View for all wallets views."""

    async def get_wallet(self, user, currency) -> Wallet:
        """Return wallet object for user_id."""
        try:
            return Wallet.get(user=user, currency=currency)
        except Wallet.DoesNotExist:
            # if trying to top-up wallet with wrong currency
            raise web.HTTPBadRequest(text='Wallet for that currency does not exist.')

    async def data_validate(self, data: JSON, request) -> JSON:
        """Additional validate data."""
        try:
            value = Decimal(data['value'])
        except InvalidOperation:
            raise web.HTTPBadRequest(text='Bad value.')
        if value <= 0:
            raise web.HTTPBadRequest(text='Value should be a positive.')
        data['value'] = value
        if data['currency'] not in {c[0] for c in CURRENCIES}:
            raise web.HTTPBadRequest(text='Bad currency.')
        return data

    async def is_double(self, trx_from: t.Optional[Wallet], trx_to: Wallet, **kwargs) -> bool:
        """Check if transaction was created recently."""
        recently = datetime.datetime.now() - datetime.timedelta(seconds=DOUBLE_TRANSACTION_CHECK_TIMEOUT)
        kwargs_conditions = [(getattr(Transaction, k) == v) for k, v in kwargs.items()]
        return Transaction.select()\
            .where(
                Transaction.trx_from == trx_from,
                Transaction.trx_to == trx_to,
                *kwargs_conditions)\
            .where(Transaction.datetime >= recently)\
            .exists()


class TransferView(BaseWalletView):
    """View for money transfers."""

    async def get_wallet_from_user_name(self, name: str, currency: str) -> Wallet:
        """Return wallet object for user with name `name`."""
        wallet = Wallet.select().join(User).where(User.name == name, Wallet.currency == currency).first()
        if not wallet:
            raise web.HTTPBadRequest(text='This user doesnt have a wallet with that currency.')
        return wallet

    async def data_validate(self, data: JSON, request) -> JSON:
        """Override base data_validate."""
        data = await super().data_validate(data, request)
        if data['to_name'] == request.user.name:
            raise web.HTTPBadRequest(text='Cant make transfer to self.')
        return data

    @login_required
    @validate(request_schema=TRANSFER_SCHEMA)
    async def post(self, data, request):
        """Send money to another user by users` name."""
        data = await self.data_validate(data, request)
        currency = data['currency']
        value = data['value']
        wallet_from = await self.get_wallet(request.user, currency=currency)
        wallet_to = await self.get_wallet_from_user_name(data['to_name'], currency=currency)
        if await self.is_double(trx_from=wallet_from, trx_to=wallet_to, value=value):
            logger.info(f'Double transfer requests: '
                        f'from: {request.user.name}, to: {data["to_name"]}, value: {value}, currency: {currency}')
            raise web.HTTPOk()
        try:
            await wallet_from.make_transfer(wallet_to, value)
        except (BalanceTooLow, WrongCurrency, WrongAmount) as e:
            raise web.HTTPBadRequest(text=str(e))
        except WalletOperationException as e:
            raise web.HTTPInternalServerError(text=str(e))
        raise web.HTTPOk()


class TopUpWallet(BaseWalletView):
    """View for top up wallet."""

    @login_required
    @validate(request_schema=WALLET_TOP_UP_SCHEMA)
    async def post(self, data, request):
        """Update wallet balance and create new row in Transactions."""
        data = await self.data_validate(data, request)
        value, currency = data['value'], data['currency']
        wallet = await self.get_wallet(request.user.id, currency)
        if await self.is_double(trx_from=None, trx_to=wallet, value=value):
            logger.info(f'Double top up requests: '
                        f'to: {request.user.name}, value: {value}, currency: {currency}')
            raise web.HTTPOk()
        try:
            await wallet.top_up(value)
        except (WrongCurrency, WrongAmount) as e:
            raise web.HTTPBadRequest(text=str(e))
        except WalletOperationException as e:
            raise web.HTTPInternalServerError(text=str(e))
        raise web.HTTPOk()
