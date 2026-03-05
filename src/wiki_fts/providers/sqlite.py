import re

from django.db import connection
from django.db.models import QuerySet
from django.db.models.sql.query import RawSQL
from django.db.utils import DatabaseError
from wiki.models import Article

from wiki_fts.providers.base import SearchProvider


class SqliteProvider(SearchProvider):
    def search(self, articles: QuerySet, query: str) -> QuerySet:
        if not query.strip():
            return articles.none()

        sql = (
            "SELECT rank FROM wiki_fts_fts5_index "
            "WHERE rowid = wiki_article.id AND wiki_fts_fts5_index MATCH %s"
        )

        try:
            qs = (
                Article.objects.annotate(rank=RawSQL(sql, [query]))
                .filter(rank__isnull=False)
                .order_by("rank")
            )
            # Force evaluate to throw error
            list(qs[:1])
            return qs
        except DatabaseError:
            # Extract all words to prevent fts5 syntax error
            safe_query = " ".join(re.findall(r"\w+", query))
            if not safe_query:
                return articles.none()
            return (
                Article.objects.annotate(rank=RawSQL(sql, [safe_query]))
                .filter(rank__isnull=False)
                .order_by("rank")
            )

    def update_index(self, article: Article):
        if connection.vendor != "sqlite":
            return

        revision = article.current_revision
        if not revision:
            return

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM wiki_fts_fts5_index WHERE article_id = %s", [article.pk]
            )
            cursor.execute(
                "INSERT INTO wiki_fts_fts5_index(article_id, title, content) VALUES (%s, %s, %s)",
                [article.pk, revision.title, revision.content or ""],
            )

    def delete_index(self, article: Article):
        if connection.vendor != "sqlite":
            return

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM wiki_fts_index WHERE article_id = %s",
                [article.pk],
            )
