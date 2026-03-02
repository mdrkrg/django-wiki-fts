from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from wiki_fts.providers import get_provider


@receiver(post_save, sender="wiki.ArticleRevision")
def on_revision_save(sender, instance, **kwargs):
    """Re-index after saving a revision, if it is the current revision."""
    article = instance.article
    if not article or article.current_revision_id != instance.pk:
        return
    provider = get_provider()
    provider.update_index(article)


@receiver(post_delete, sender="wiki.ArticleRevision")
def on_revision_delete(sender, instance, **kwargs):
    """Remove index when a revision is hard-deleted."""
    try:
        article = instance.article
    except Exception:
        return  # Article already deleted
    if article and article.current_revision_id == instance.pk:
        provider = get_provider()
        provider.delete_index(article)


@receiver(post_delete, sender="wiki.Article")
def on_article_delete(sender, instance, **kwargs):
    """Remove index when an article is hard-deleted."""
    provider = get_provider()
    provider.delete_index(instance)
