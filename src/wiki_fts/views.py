from django.db.models import QuerySet
from django.http import Http404
from wiki import models
from wiki.core import permissions
from wiki.core.exceptions import NoRootURL
from wiki.views.article import SearchView

from wiki_fts.providers import get_provider


class FullTextSearchView(SearchView):
    @staticmethod
    def search(articles: QuerySet, query: str):
        """Perform search on the articles."""
        # TODO: No highlight when search query does not match result exactly
        provider = get_provider()
        return provider.search(articles, query)

    def get_queryset(self):
        if not self.query:
            return models.Article.objects.none().order_by("-current_revision__created")
        articles = models.Article.objects
        path = self.kwargs.get("path", None)
        if path:
            try:
                self.urlpath = models.URLPath.get_by_path(path)
                article_ids = self.urlpath.get_descendants(
                    include_self=True
                ).values_list("article_id")
                articles = articles.filter(id__in=article_ids)
            except (NoRootURL, models.URLPath.DoesNotExist):
                raise Http404
        articles = self.search(articles, self.query)
        if not permissions.can_moderate(
            models.URLPath.root().article, self.request.user
        ):
            articles = articles.active().can_read(self.request.user)
        return articles.order_by("-current_revision__created")
