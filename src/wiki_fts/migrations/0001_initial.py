import django.db.models.deletion
from django.db import migrations, models

import wiki_fts.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wiki", "0003_mptt_upgrade"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchIndex",
            fields=[
                (
                    "article",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="search_index",
                        serialize=False,
                        to="wiki.article",
                    ),
                ),
                ("search_vector", wiki_fts.models.ConditionalSearchVectorField()),
                ("language", models.CharField(default="simple", max_length=50)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
