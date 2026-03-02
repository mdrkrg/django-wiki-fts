from django.apps import AppConfig


class WikiConfig(AppConfig):
    default_site = "wiki_fts.sites.WikiSite"
    default_auto_field = "django.db.models.AutoField"
    name = "wiki_fts"

    def ready(self):
        import wiki_fts.signals  # noqa: F401
        from wiki.sites import site
        from wiki_fts.sites import WikiSite

        # HACK: Inject site to override
        site._wrapped = WikiSite()
