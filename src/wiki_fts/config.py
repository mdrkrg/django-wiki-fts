from django.conf import settings

PROVIDER = getattr(settings, "WIKI_FTS_PROVIDER", "wiki_fts.providers.BasicProvider")
"""Full-text search provider."""

DEFAULT_LANGUAGE = getattr(settings, "WIKI_FTS_DEFAULT_LANGUAGE", "simple")
"""Default language for SearchIndex. Only applicable to PostgresProvider."""

SQLITE_TOKENIZE = getattr(settings, "WIKI_FTS_SQLITE_TOKENIZE", "unicode61")
