import pytest
from wiki.models import Article, ArticleRevision


@pytest.mark.django_db
def test_article_creation():
    """Verify test infrastructure works."""
    article = Article.objects.create()
    revision = ArticleRevision.objects.create(article=article, title="Hello")
    article.add_revision(revision)

    article.refresh_from_db()
    assert article.current_revision.title == "Hello"
