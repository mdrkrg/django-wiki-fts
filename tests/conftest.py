import logging
import os
from unittest.mock import MagicMock

import psycopg
import pytest
from psycopg import sql

from wiki_fts.providers.base import SearchProvider

# Database setup

DB_NAME = os.getenv("DB_NAME", "wiki_fts_test")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")


logger = logging.getLogger(__name__)


def _admin_conn():
    """Open an connection to the 'postgres' maintenance database."""
    conn = psycopg.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        autocommit=True,
    )
    return conn


def pytest_configure(config):
    """Create the test database."""
    conn = _admin_conn()
    try:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        logger.info(f"\nCreated test database: {DB_NAME}")
    except psycopg.errors.DuplicateDatabase:
        logger.error(f"\nTest database already exists: {DB_NAME}")
    finally:
        conn.close()


def pytest_unconfigure(config):
    """Drop the test database after tests finish."""
    conn = _admin_conn()
    try:
        # Terminate remaining connections
        conn.execute(
            sql.SQL(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = {db} AND pid <> pg_backend_pid()
                """
            ).format(db=sql.Literal(DB_NAME))
        )
        conn.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME))
        )
        logger.info(f"\nDropped test database: {DB_NAME}")
    finally:
        conn.close()


@pytest.fixture(autouse=True)
def mock_provider(monkeypatch):
    """Replace get_provider() with a Mock."""
    mock = MagicMock(spec=SearchProvider)

    monkeypatch.setattr("wiki_fts.signals.get_provider", lambda: mock)
    monkeypatch.setattr("wiki_fts.views.get_provider", lambda: mock)
    monkeypatch.setattr(
        "wiki_fts.management.commands.wiki_rebuild_index.get_provider",
        lambda: mock,
    )

    return mock
