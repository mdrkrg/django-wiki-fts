from io import StringIO

import pytest
from django.core.management import call_command
from wiki.models import Article, ArticleRevision

NAME = "wiki_rebuild_index"


@pytest.mark.django_db
def test_wiki_rebuild_index_command_indexes_all_articles(mock_provider):
    """
    The `wiki_rebuild_index` command must call `provider.update_index`
    for each article in the database.
    """
    for i in range(3):
        article = Article.objects.create()
        revision = ArticleRevision(article=article, title=f"Article {i}")
        article.add_revision(revision)

    mock_provider.reset_mock()

    out = StringIO()
    call_command(NAME, stdout=out)

    assert mock_provider.update_index.call_count == 3
    for call in mock_provider.update_index.call_args_list:
        assert isinstance(call[0][0], Article)
    assert "Updated 3 article indexes." in out.getvalue()


@pytest.mark.django_db
def test_wiki_rebuild_index_command_with_no_articles(mock_provider):
    """
    When database is empty, `wiki_rebuild_index` do nothing.
    """
    mock_provider.reset_mock()

    out = StringIO()
    call_command(NAME, stdout=out)

    mock_provider.update_index.assert_not_called()

    assert "No articles to update." in out.getvalue()
