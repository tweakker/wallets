from .views import TransferView, TopUpWallet

routes = [
    {'method': 'POST', 'path': '/api/wallet/', 'handler': TopUpWallet, 'name': 'wallet-top-up'},
    {'method': 'POST', 'path': '/api/wallet/transfer/', 'handler': TransferView, 'name': 'wallet-transfer'},
]