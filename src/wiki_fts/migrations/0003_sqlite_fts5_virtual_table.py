from django.db import migrations

from wiki_fts import config


def create_sqlite_fts5_virtual_table(apps, schema_editor):
    """
    Create SQLite FTS5 virtual table.
    """
    if schema_editor.connection.vendor != "sqlite":
        return

    # Create FTS5 virtual table
    schema_editor.execute(f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts_fts5_index
        USING fts5(
            article_id UNINDEXED,
            title,
            content,
            tokenize='{config.SQLITE_TOKENIZE}'
        );
    """)


def drop_sqlite_fts5_virtual_table(apps, schema_editor):
    """
    Create SQLite FTS5 virtual table.
    """
    if schema_editor.connection.vendor != "sqlite":
        return

    schema_editor.execute("DROP TABLE IF EXISTS wiki_fts_fts5_index;")


class Migration(migrations.Migration):
    dependencies = [
        ("wiki_fts", "0002_postgres_gin_index"),
    ]

    operations = [
        migrations.RunPython(
            create_sqlite_fts5_virtual_table,
            drop_sqlite_fts5_virtual_table,
        ),
    ]
