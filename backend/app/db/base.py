from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base all ORM models inherit from; collects table metadata for migrations."""
