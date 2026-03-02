from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from django.db.models import F, QuerySet, Value
from wiki.models import Article

from wiki_fts.models import SearchIndex
from wiki_fts.providers.base import SearchProvider


class PostgresProvider(SearchProvider):
    def search(self, articles: QuerySet, query: str):
        q = SearchQuery(
            query,
            config=F("search_index__language"),
            search_type="websearch",
        )
        articles = articles.filter(search_index__search_vector=q)
        annotate = articles.annotate(rank=SearchRank("search_index__search_vector", q))
        return annotate.order_by("-rank")

    def update_index(self, article: Article):
        if connection.vendor != "postgresql":
            return

        revision = article.current_revision
        if not revision:
            return

        search_index, _ = SearchIndex.objects.get_or_create(article=article)

        SearchIndex.objects.filter(pk=article.pk).update(
            search_vector=(
                SearchVector(
                    Value(revision.title),
                    weight="A",
                    config=search_index.language,
                )
                + SearchVector(
                    Value(revision.content),
                    weight="B",
                    config=search_index.language,
                )
            )
        )

    def delete_index(self, article: Article):
        # Deletion is handled by cascade
        pass
