from django.conf import settings

PROVIDER = getattr(settings, "WIKI_FTS_PROVIDER", "wiki_fts.providers.BasicProvider")
"""Full-text search provider."""
