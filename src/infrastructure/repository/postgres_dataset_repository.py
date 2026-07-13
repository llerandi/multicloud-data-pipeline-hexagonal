"""PostgresDatasetRepository: a DatasetRepository adapter backed by Postgres.

This module does not import psycopg, or any other driver, at all. It
only calls .cursor(), .executemany() and .commit() on whatever
connection object it is given, the same methods any DB-API 2.0
compatible connection exposes. The actual psycopg dependency only shows
up wherever a real connection gets constructed and handed to this
class, not here, which is what keeps this adapter fully testable with a
plain fake object instead of a real database.
"""

from typing import Any, Mapping, Sequence

from src.application.ports import DatasetRepository


def _quote_identifier(name: str) -> str:
    """Quote a SQL identifier (a table or column name) safely.

    Parameterized placeholders (the %s used below) only work for
    values, never for identifiers, a driver will not let you bind a
    table name as a parameter. Wrapping the name in double quotes, and
    doubling any double quote already inside it, is the standard SQL
    way to make an identifier safe to interpolate directly into a
    query string. dataset_name reaches this repository already having
    passed through the pipeline, but treating it as trusted input would
    be exactly the kind of assumption that stops being true the day
    this project accepts a dataset_name from somewhere less controlled.
    """
    return '"' + name.replace('"', '""') + '"'


class PostgresDatasetRepository(DatasetRepository):
    """Saves rows into a Postgres table using a caller-supplied connection.

    connection is expected to already be open and configured (host,
    credentials, database) by whoever constructs this class, this
    adapter does not manage connection setup or its lifecycle, only
    what to do with rows once it has one. That mirrors LocalFileStorage
    taking root_dir already resolved, and SklearnModelInference taking
    an already-fitted model: each adapter is handed a ready-to-use
    collaborator, not the configuration needed to build one.
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def save(self, dataset_name: str, rows: Sequence[Mapping[str, Any]]) -> None:
        """Insert rows into the table named dataset_name.

        Does nothing for an empty sequence of rows, rather than
        raising, there is no column list to infer an INSERT statement
        from without at least one row, and "nothing to write" is not
        an error condition on its own.

        Column names come from the first row's keys, every row is
        expected to share the same columns, a row missing a key raises
        a plain KeyError, the same "let a clear standard library error
        propagate" choice made in LocalFileStorage and the use case's
        file parsing.
        """
        if not rows:
            return

        columns = list(rows[0].keys())
        quoted_table = _quote_identifier(dataset_name)
        quoted_columns = ", ".join(_quote_identifier(column) for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        query = (
            f"INSERT INTO {quoted_table} ({quoted_columns}) "
            f"VALUES ({placeholders})"
        )
        values = [tuple(row[column] for column in columns) for row in rows]

        with self._connection.cursor() as cursor:
            cursor.executemany(query, values)
        self._connection.commit()
