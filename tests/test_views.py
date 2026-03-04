import pytest
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import RequestFactory
from wiki.models import Article, ArticleRevision, URLPath

from wiki_fts.views import FullTextSearchView


@pytest.fixture(autouse=True)
def wiki_root():
    """Create a root URLPath for Django Wiki."""
    site = Site.objects.get_current()
    root_article = Article.objects.create()
    root_revision = ArticleRevision(article=root_article, title="Root")
    root_article.add_revision(root_revision)

    root_path = URLPath.objects.create(
        site=site,
        article=root_article,
        slug="",
    )
    return root_path


@pytest.mark.django_db
def test_search_view_calls_provider_search(mock_provider):
    """
    `FullTextSearchView.get_queryset` must call `provider.search`
    with the articles queryset and search query.
    """
    article = Article.objects.create()
    revision = ArticleRevision(article=article, title="Test Article")
    article.add_revision(revision)

    # Mock return the queryset
    mock_provider.search.return_value = Article.objects.filter(id=article.id)

    # Create request
    factory = RequestFactory()
    request = factory.get("/search/?q=test")
    request.user = User.objects.create_user(username="testuser")

    view = FullTextSearchView()
    view.request = request
    view.query = "test"
    view.kwargs = {}

    mock_provider.reset_mock()
    mock_provider.search.return_value = Article.objects.filter(id=article.id)

    # Execute search
    view.get_queryset()

    # SearchProvider.search
    mock_provider.search.assert_called_once()

    # Search query
    call_args = mock_provider.search.call_args
    assert call_args[0][1] == "test"


@pytest.mark.django_db
def test_search_view_empty_query_returns_none(mock_provider):
    """
    When query is empty, `get_queryset` should return an empty queryset
    without calling `provider.search`.
    """
    factory = RequestFactory()
    request = factory.get("/search/?q=")
    request.user = User.objects.create_user(username="testuser")

    view = FullTextSearchView()
    view.request = request
    view.query = ""
    view.kwargs = {}

    mock_provider.reset_mock()

    view.get_queryset()

    mock_provider.search.assert_not_called()
