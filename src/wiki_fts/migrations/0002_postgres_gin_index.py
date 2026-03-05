from django.db import migrations
from django.db.migrations.operations.special import SeparateDatabaseAndState

import wiki_fts.models


def add_postgres_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS wiki_fts_gin_index "
        "ON wiki_fts_searchindex USING GIN (search_vector);"
    )


def remove_postgres_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP INDEX IF EXISTS wiki_fts_gin_index;")


class Migration(migrations.Migration):
    dependencies = [
        ("wiki_fts", "0001_initial"),
    ]

    operations = [
        SeparateDatabaseAndState(
            state_operations=[
                migrations.AddIndex(
                    model_name="searchindex",
                    index=wiki_fts.models.ConditionalGinIndex(
                        fields=["search_vector"], name="wiki_fts_gin_index"
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_postgres_index,
                    remove_postgres_index,
                ),
            ],
        ),
    ]
