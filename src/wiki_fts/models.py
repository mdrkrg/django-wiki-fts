from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from wiki.models import Article


class ConditionalSearchVectorField(SearchVectorField):
    def db_type(self, connection):  # type: ignore
        if connection.vendor == "postgresql":
            return "tsvector"
        return "text"


class ConditionalGinIndex(GinIndex):
    """GinIndex that only creates on Postgres."""

    def create_sql(self, model, schema_editor, using="", **kwargs):
        if schema_editor.connection.vendor != "postgresql":
            return None
        return super().create_sql(model, schema_editor, using, **kwargs)


class SearchIndex(models.Model):
    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name="search_index",
        primary_key=True,
    )
    search_vector = ConditionalSearchVectorField()
    language = models.CharField(max_length=50, default="simple")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            ConditionalGinIndex(fields=["search_vector"], name="wiki_fts_gin_index"),
        ]
