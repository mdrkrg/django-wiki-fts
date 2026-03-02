from django.db.utils import import_string

from wiki_fts.providers.base import SearchProvider
from wiki_fts.providers.basic import BasicProvider
from wiki_fts.providers.postgres import PostgresProvider
from wiki_fts import config


_active: SearchProvider | None = None


def get_provider() -> SearchProvider:
    """Return the active provider"""
    global _active
    if _active is not None:
        return _active

    cls = import_string(config.PROVIDER)
    _active = cls()
    return _active


__all__ = [
    "BasicProvider",
    "PostgresProvider",
    "get_provider",
]
