from backend.apps.wallets.models import Wallet, Transaction
from backend.apps.users.models import User


MODELS = [User, Wallet, Transaction]


def db_init(app):
    app.db.create_tables(MODELS, safe=True)

def db_clear(app):
    app.db.drop_tables(reversed(MODELS), safe=True)


if __name__ == '__main__':
    import peewee
    import time
    from backend.app import app

    CONNECTIONS_TRIES_LIMIT = 15
    counter = 0
    while True:
        try:
            db_init(app)
        except peewee.DatabaseError:
            print('Waiting for database...')
            counter += 1
            if counter == CONNECTIONS_TRIES_LIMIT:
                print('Database is not available.')
                break
            time.sleep(1)
        else:
            break

