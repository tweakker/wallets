import datetime
from decimal import Decimal

import peewee

from backend.logger import logger
from backend.db import BaseModel, database
from backend.apps.users.models import User
from .enums import CURRENCIES, USD
from .exceptions import *


class Wallet(BaseModel):
    """Model for users wallet."""

    user = peewee.ForeignKeyField(User, on_delete='SET NULL', null=True)
    balance = peewee.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=True)
    currency = peewee.CharField(max_length=4, choices=CURRENCIES, default=USD, index=True)

    async def top_up(self, value: Decimal):
        """Top up wallet balance."""
        cls = self.__class__
        with database.atomic() as transaction:
            try:
                cls.update(balance=cls.balance + value).where(cls.id == self.id).execute()
                Transaction.create(trx_to=self, value=value, currency=self.currency)
            except peewee.DatabaseError:
                transaction.rollback()
                logger.exception(f'Rollback from {self} top up transaction.')
                raise WalletOperationException

    def _transfer_prevalidate(self, _to, value):
        """Validate data before transfer."""
        if value <= 0:
            raise WrongAmount
        if value > self.balance:
            raise BalanceTooLow
        if _to.currency != self.currency:
            raise WrongCurrency

    async def make_transfer(self, _to: 'Wallet', value: Decimal):
        """Send money to another wallet."""
        cls = self.__class__
        self._transfer_prevalidate(_to, value)
        with database.atomic() as transaction:
            try:
                cls.update(balance=cls.balance - value).where(cls.id == self.id).execute()
                _updated = await self.refresh()
                if _updated.balance < 0:
                    # if another transaction changed balance before and balance is to low now
                    # rollback it
                    transaction.rollback()
                    logger.exception(f'Rollback from {self} transfer transaction: balance lower than 0.')
                    raise BalanceTooLow
                cls.update(balance=cls.balance + value).where(cls.id == _to.id).execute()
                Transaction.create(trx_from=self, trx_to=_to, value=value, currency=self.currency)
            except peewee.DatabaseError:
                transaction.rollback()
                logger.exception(f'Rollback from {self} transfer transaction.')
                raise WalletOperationException


class Transaction(BaseModel):
    """Model for transactions.

    - `trx_from`: can be null, it means top up balance from user.
    """

    trx_from = peewee.ForeignKeyField(Wallet, null=True, index=True)
    trx_to = peewee.ForeignKeyField(Wallet, index=True)
    value = peewee.DecimalField(max_digits=12, decimal_places=2)
    datetime = peewee.DateTimeField(default=datetime.datetime.now, index=True)
