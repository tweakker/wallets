
class WalletOperationException(Exception):
    text = 'Wallet operation error.'

    def __str__(self):
        return getattr(self, 'text')


class BalanceTooLow(WalletOperationException):
    text = 'Balance is too low.'


class WrongCurrency(WalletOperationException):
    text = 'Wrong wallet currency value.'


class WrongAmount(WalletOperationException):
    text = 'Wrong amount value.'
