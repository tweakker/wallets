from backend.apps.wallets.models import Wallet, Transaction
from backend.apps.users.models import User
from backend.db import database

MODELS = [User, Wallet, Transaction]


def db_init():
    database.create_tables(MODELS, safe=True)


def db_clear():
    database.drop_tables(reversed(MODELS), safe=True)


if __name__ == '__main__':
    import peewee
    import time

    CONNECTIONS_TRIES_LIMIT = 15
    counter = 0
    while True:
        try:
            db_init()
        except peewee.DatabaseError:
            print('Waiting for database...')
            counter += 1
            if counter == CONNECTIONS_TRIES_LIMIT:
                print('Database is not available.')
                break
            time.sleep(1)
        else:
            break

