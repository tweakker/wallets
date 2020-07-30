import peewee

from . import settings


database = peewee.PostgresqlDatabase(
    settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    autorollback=True,
)


class BaseModel(peewee.Model):
    """Base model for all models."""

    class Meta:
        database = database

    def refresh(self):
        """Refresh object from db."""
        return type(self).get_by_id(self._pk)
