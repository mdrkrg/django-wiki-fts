from django.core.management.base import BaseCommand
from django.db import transaction
from wiki.models import Article

from wiki_fts.providers import get_provider


class Command(BaseCommand):
    help = "Rebuild wiki article search indexes"

    def handle(self, *args, **options):
        articles = Article.objects.all()
        provider = get_provider()
        try:
            with transaction.atomic():
                for article in articles:
                    provider.update_index(article)
            self.stdout.write(
                self.style.SUCCESS(f"Updated {articles.count()} article indexes.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to update article indexes: {e}")
            )
