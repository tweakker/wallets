from backend.apps.wallets.models import Wallet, Transaction
from backend.apps.users.models import User


MODELS = [User, Wallet, Transaction]


def db_init(app):
    app.db.create_tables(MODELS, safe=True)

def db_clear(app):
    app.db.drop_tables(reversed(MODELS), safe=True)


# creating db tables
if __name__ == '__main__':
    from backend.app import app
    db_init(app)
