from os import environ

# db settings
DB_USER = environ.get('POSTGRES_USER', 'user')
DB_PASSWORD = environ.get('POSTGRES_PASSWORD', 'password')
DB_HOST = environ.get('POSTGRES_HOST', 'wallets_db')
DB_NAME = environ.get('POSTGRES_DB', 'db')
TEST_DATABASE_NAME = environ.get('TEST_DATABASE_NAME', 'test')

SECRET_KEY = 'GkZup9wI8zXDTKnviqOk'

# debug
DEBUG = False

# time in seconds between doubles transaction are ignored
DOUBLE_TRANSACTION_CHECK_TIMEOUT = 5


