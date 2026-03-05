from importlib import reload

import pytest
from django.test import override_settings
from wiki.models import Article, ArticleRevision

from wiki_fts import config
from wiki_fts.models import SearchIndex
from wiki_fts.providers.postgres import PostgresProvider


@pytest.mark.django_db
def test_postgres_provider_uses_default_language():
    """
    `PostgresProvider.update_index` should create a SearchIndex with
    the language from config.DEFAULT_LANGUAGE (default: "simple").
    """
    provider = PostgresProvider()

    article = Article.objects.create()
    revision = ArticleRevision(
        article=article, title="Test Article", content="Test content"
    )
    article.add_revision(revision)

    # Call provider explicitly
    provider.update_index(article)

    search_index = SearchIndex.objects.get(article=article)
    assert search_index.language == "simple"


@pytest.mark.django_db
@override_settings(WIKI_FTS_DEFAULT_LANGUAGE="english")
def test_postgres_provider_creates_with_custom_language():
    """
    `PostgresProvider.update_index` should create index with the language
    set in `WIKI_FTS_DEFAULT_LANGUAGE` setting.
    """
    reload(config)

    provider = PostgresProvider()

    article = Article.objects.create()
    revision = ArticleRevision(
        article=article, title="Test Article", content="Test content"
    )
    article.add_revision(revision)

    provider.update_index(article)

    search_index = SearchIndex.objects.get(article=article)
    assert search_index.language == "english"


@pytest.mark.django_db
def test_postgres_provider_preserves_language_on_update():
    """
    When updating an existing SearchIndex, the language should be preserved
    (not reset to default).
    """
    provider = PostgresProvider()

    article = Article.objects.create()
    revision = ArticleRevision(article=article, title="First", content="Content")
    article.add_revision(revision)

    # Create initial index and change language
    provider.update_index(article)
    search_index = SearchIndex.objects.get(article=article)
    search_index.language = "arabic"
    search_index.save()

    # Update the article
    new_revision = ArticleRevision(
        article=article, title="Second", content="New content"
    )
    article.add_revision(new_revision)
    provider.update_index(article)

    # Language should be preserved
    search_index.refresh_from_db()
    assert search_index.language == "arabic"
