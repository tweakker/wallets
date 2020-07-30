import logging

from backend import settings


logger = logging.getLogger('wallet_web')

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
