import os

import nox

nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
DJANGO_VERSIONS = ["4.0", "4.1", "4.2", "5.1", "5.2"]

pyproject = nox.project.load_toml()
test_requirements = nox.project.dependency_groups(pyproject, "test")
lint_requirements = nox.project.dependency_groups(pyproject, "lint")


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("django", DJANGO_VERSIONS)
def tests(session, django):
    """Run tests against a matrix of Python and Django versions."""
    session.install(*test_requirements)
    session.install(f"django~={django}")
    session.install("wiki>=0.10,<0.13")

    session.install("-e", ".")

    # Load environment
    env = os.environ.copy()
    env.update(
        {
            "DJANGO_SETTINGS_MODULE": "tests.settings",
            "DB_USER": os.getenv("DB_USER", "postgres"),
            "DB_PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "DB_HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "DB_PORT": os.getenv("DB_PORT", "5432"),
        }
    )

    # Run tests
    session.run("pytest", env=env)


@nox.session
def lint(session):
    """Run ruff check."""
    session.install(*lint_requirements)
    session.run("ruff", "check")


@nox.session
def format(session):
    """Check ruff format."""
    session.install(*lint_requirements)
    session.run("ruff", "format", "--check", "--diff")
