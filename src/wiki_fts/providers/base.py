import abc

from django.db.models import QuerySet
from wiki.models import Article


class SearchProvider(abc.ABC):
    """Full-text search provider interface"""

    @abc.abstractmethod
    def search(self, articles: QuerySet, query: str) -> QuerySet: ...

    @abc.abstractmethod
    def update_index(self, article: Article): ...

    @abc.abstractmethod
    def delete_index(self, article: Article): ...
