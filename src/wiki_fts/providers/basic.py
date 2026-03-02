from django.db.models import Q, QuerySet
from wiki.models import Article

from wiki_fts.providers.base import SearchProvider


class BasicProvider(SearchProvider):
    def search(self, articles: QuerySet, query: str):
        return articles.filter(
            Q(current_revision__title__icontains=query)
            | Q(current_revision__content__icontains=query)
        )

    def update_index(self, article: Article):
        pass

    def delete_index(self, article: Article):
        pass
