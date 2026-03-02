from django.apps import AppConfig


class WikiConfig(AppConfig):
    default_site = "wiki_fts.sites.WikiSite"
    default_auto_field = "django.db.models.AutoField"
    name = "wiki_fts"
