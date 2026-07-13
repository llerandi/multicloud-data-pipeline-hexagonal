"""Unit tests for PostgresDatasetRepository.

FakeConnection and FakeCursor below implement just enough of the
DB-API 2.0 shape (cursor() as a context manager, executemany, commit)
to stand in for a real psycopg connection. Since the adapter itself
never imports psycopg, none of these tests need it installed either,
they exercise the adapter's own logic: how it builds the query and
what it does with an empty dataset.
"""

import pytest

from src.application.ports import DatasetRepository
from src.infrastructure.repository.postgres_dataset_repository import (
    PostgresDatasetRepository,
    _quote_identifier,
)


class FakeCursor:
    def __init__(self):
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def executemany(self, query, values):
        self.executed.append((query, values))


class FakeConnection:
    def __init__(self):
        self.cursor_used = FakeCursor()
        self.committed = False

    def cursor(self):
        return self.cursor_used

    def commit(self):
        self.committed = True


def test_postgres_dataset_repository_is_a_dataset_repository():
    assert issubclass(PostgresDatasetRepository, DatasetRepository)


def test_quote_identifier_wraps_a_plain_name_in_double_quotes():
    assert _quote_identifier("customers") == '"customers"'


def test_quote_identifier_escapes_an_embedded_double_quote():
    # A contrived, adversarial table name, this is exactly the case
    # naive string interpolation would get wrong.
    assert _quote_identifier('cust"omers') == '"cust""omers"'


def test_save_does_nothing_for_an_empty_list_of_rows():
    connection = FakeConnection()
    repository = PostgresDatasetRepository(connection)

    repository.save("customers", [])

    assert connection.cursor_used.executed == []
    assert connection.committed is False


def test_save_builds_a_parameterized_query_with_quoted_identifiers():
    connection = FakeConnection()
    repository = PostgresDatasetRepository(connection)

    repository.save(
        "customers",
        [{"id": "1", "email": "a@b.com"}, {"id": "2", "email": "c@d.com"}],
    )

    assert len(connection.cursor_used.executed) == 1
    query, values = connection.cursor_used.executed[0]
    assert query == 'INSERT INTO "customers" ("id", "email") VALUES (%s, %s)'
    assert values == [("1", "a@b.com"), ("2", "c@d.com")]
    assert connection.committed is True


def test_save_raises_a_key_error_if_a_later_row_is_missing_a_column():
    connection = FakeConnection()
    repository = PostgresDatasetRepository(connection)

    with pytest.raises(KeyError):
        repository.save(
            "customers",
            [{"id": "1", "email": "a@b.com"}, {"id": "2"}],
        )
