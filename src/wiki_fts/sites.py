from wiki.sites import WikiSite as OriginalWikiSite

from wiki_fts.views import FullTextSearchView


class WikiSite(OriginalWikiSite):
    def __init__(self, name="wiki"):
        self.search_view = FullTextSearchView.as_view()
        super().__init__(name)
