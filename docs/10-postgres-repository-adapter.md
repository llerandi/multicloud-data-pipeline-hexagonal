# PR 10: PostgresDatasetRepository adapter

Branch: `feature/postgres-repository-adapter`

Files added: `src/infrastructure/repository/postgres_dataset_repository.py`,
`src/infrastructure/repository/__init__.py` (updated),
`tests/infrastructure/repository/test_postgres_dataset_repository.py`,
`pyproject.toml` (updated).

## Why this adapter never imports psycopg

```python
"""
This module does not import psycopg, or any other driver, at all. It
only calls .cursor(), .executemany() and .commit() on whatever
connection object it is given, the same methods any DB-API 2.0
compatible connection exposes.
"""
```

Every Python database driver (`psycopg`, `sqlite3`, `pymysql`, and others)
implements the same DB-API 2.0 shape: a connection object with `.cursor()`
and `.commit()`, a cursor with `.execute()` or `.executemany()`. This
adapter is written against that shape, not against `psycopg` specifically,
by only ever calling those methods on `self._connection`, never importing
the `psycopg` package itself. The real dependency only shows up wherever
a real connection actually gets constructed (`psycopg.connect(...)`), and
that is deliberately left outside this class, which is what the
constructor's docstring means by "this adapter does not manage connection
setup or its lifecycle". The practical effect: this file, and every test
in this PR, works without `psycopg` installed at all, the same reasoning
`SklearnModelInference` used for a model instead of a database
connection.

## Why identifiers are quoted by hand instead of using f-strings, and why that is not the same problem parameterized values solve

```python
def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'
```

```python
placeholders = ", ".join(["%s"] * len(columns))
query = f"INSERT INTO {quoted_table} ({quoted_columns}) VALUES ({placeholders})"
```

There are two different categories of untrusted string in this query,
and they are handled two different ways on purpose. The actual row
values go through `%s` placeholders and `cursor.executemany`, letting the
driver handle escaping, this is the standard, safe way to put values into
a SQL query, and it is why `dataset_name` and `rows` never get formatted
directly into the value side of the string.

Table and column names are a different category: parameterized
placeholders only work for values, no driver lets you bind a table name
as a query parameter, `%s` there would produce invalid SQL, not a safely
escaped identifier. `_quote_identifier` exists to handle that other
category by hand, wrapping the name in double quotes and doubling any
double quote already inside it, which is the standard SQL way to make an
identifier safe to interpolate directly. Skipping this and writing
`f"INSERT INTO {dataset_name} ..."` directly would work for a table named
`customers`, and would also happily execute whatever a table named
`customers; DROP TABLE customers; --` decided to be. `dataset_name`
reaches this repository already having passed through the rest of the
pipeline today, but treating it as trusted because of that is exactly
the kind of assumption that quietly stops being true the day this
project accepts it from somewhere less controlled.

## Why the constructor takes an already-open connection, not a connection string

```python
def __init__(self, connection: Any) -> None:
    self._connection = connection
```

Same reasoning as `LocalFileStorage` taking `root_dir` already resolved
and `SklearnModelInference` taking an already-fitted model: this class is
handed a ready-to-use collaborator, it does not know how to build one
itself. Constructing a real connection needs a host, credentials, and a
database name, configuration this adapter has no business owning, that
belongs to whatever composition code wires the pipeline together for a
specific environment. It is also what makes `FakeConnection` in the test
file a legitimate stand-in instead of a compromise: the real class never
does anything with `connection` beyond calling the three DB-API methods
it needs.

## Why `save` does nothing for an empty list of rows, and why a missing column raises `KeyError`

```python
if not rows:
    return
```

An `INSERT` statement's column list is inferred from the first row's
keys, there is no column list to infer from zero rows, so an empty
dataset means nothing to write, not an error, matching the same choice
`DataQualityReport.null_ratio` made for an empty dataset in the domain
layer.

A later row missing a key that the first row had is not specially
handled, `row[column]` raises a plain `KeyError` naming the missing key.
This is the same pattern used for a missing file in `LocalFileStorage`
and for a badly shaped dataset file in the use case's parsing: a clear,
standard exception that already says what went wrong, rather than a
custom exception type that would only repeat the same information in a
different shape.

## Why the tests do not need a real Postgres database, and what is still missing

Every test in `test_postgres_dataset_repository.py` uses `FakeConnection`
and `FakeCursor`, small classes that record what was called and return
canned results, exactly the DB-API surface this adapter touches. That is
enough to prove `PostgresDatasetRepository`'s own logic is correct: the
query it builds, the order values are bound in, quoting, and the empty
and missing-column edge cases, all without a database running anywhere.

What this PR does not include is a test against a real, running Postgres
instance. That would need either a live database reachable from wherever
tests run, or a service container configured in CI, neither of which
exists yet for this project. `psycopg[binary]` was still added as its own
optional extra (`postgres`, following the same pattern as `sklearn`), it
is what whoever wires this adapter into an actual pipeline run will need
to construct a real connection to hand to it, even though no code in this
PR imports it yet. Adding a real integration test, most likely backed by
a `postgres` service container in `ci.yaml`, is left as explicit future
work rather than skipped silently.
