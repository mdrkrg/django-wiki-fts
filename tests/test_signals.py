import pytest
from wiki.models import Article, ArticleRevision


def make_article_with_revision(**revision_kwargs) -> Article:
    """Create an Article and add a first revision as the current one."""
    article = Article.objects.create()
    revision = ArticleRevision(
        article=article,
        title=revision_kwargs.pop("title", "First revision"),
        **revision_kwargs,
    )
    article.add_revision(revision)
    return article


# on_revision_save


@pytest.mark.django_db
def test_revision_save_current_revision_updates_index(mock_provider):
    """
    Saving a revision that becomes the current revision should call
    `provider.update_index` with the article.
    """
    article = make_article_with_revision()

    mock_provider.update_index.assert_called_once_with(article)


@pytest.mark.django_db
def test_revision_save_non_current_revision_skips_index(mock_provider):
    """
    Saving a revision that is NOT the current revision should not call
    `provider.update_index`.
    """
    article = make_article_with_revision()
    mock_provider.reset_mock()

    # Do not make this revision current
    ArticleRevision.objects.create(article=article, title="Non-current revision")

    mock_provider.update_index.assert_not_called()


# on_revision_delete


@pytest.mark.django_db
def test_revision_delete_current_revision_removes_index(mock_provider):
    """
    Deleting the current revision cascades to the article, triggers both
    `on_revision_delete` and `on_article_delete`.
    """
    article = make_article_with_revision()
    current = article.current_revision
    mock_provider.reset_mock()

    current.delete()

    assert mock_provider.delete_index.call_count == 2
    for call in mock_provider.delete_index.call_args_list:
        assert isinstance(call[0][0], Article)


@pytest.mark.django_db
def test_revision_delete_non_current_revision_skips_index(mock_provider):
    """
    Deleting a revision that is NOT the current revision
    should not call `provider.delete_index`.
    """
    article = make_article_with_revision()
    non_current = ArticleRevision.objects.create(
        article=article,
        title="Non-current revision",
    )
    mock_provider.reset_mock()

    non_current.delete()

    mock_provider.delete_index.assert_not_called()


# on_article_delete


@pytest.mark.django_db
def test_article_delete_removes_index(mock_provider):
    """
    Deleting an article cascades to revisions, triggers both
    `on_revision_delete` and `on_article_delete`.
    """
    article = make_article_with_revision()
    mock_provider.reset_mock()

    article.delete()

    assert mock_provider.delete_index.call_count == 2
    mock_provider.delete_index.assert_called_with(article)
