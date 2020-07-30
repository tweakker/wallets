import peewee

# init database later in create_app
database = peewee.PostgresqlDatabase(None)


class BaseModel(peewee.Model):
    """Base model for all models."""

    class Meta:
        database = database

    async def refresh(self):
        """Refresh object from db."""
        return type(self).get_by_id(self._pk)
