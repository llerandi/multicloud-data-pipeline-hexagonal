# PR 13: BigqueryDatasetRepository adapter

Branch: `feature/bigquery-repository-adapter`

Files added: `src/infrastructure/repository/bigquery_dataset_repository.py`,
`src/infrastructure/repository/__init__.py` (updated),
`tests/infrastructure/repository/test_bigquery_dataset_repository.py`,
`pyproject.toml` (updated).

`DatasetRepository` now has both adapters the project scope asked for:
Postgres and BigQuery. Same port, and this time the interesting
difference is not the shape of a single call, like `FileStorage`'s pair,
it is how each system reports failure.

## A naming collision worth calling out directly

```python
"""
dataset_id is BigQuery's own "dataset", a namespace that groups tables
inside a project [...] This is an unfortunate but unavoidable name
collision: everywhere else in this project, "dataset" means the CSV or
JSON file being validated and ingested.
"""
```

BigQuery organizes tables inside a "dataset" (a namespace inside a
project, for example `analytics`), and this project has been calling the
CSV or JSON file being validated a "dataset" since the very first PR.
Those are two unrelated meanings of the same English word, one is a
BigQuery infrastructure concept, the other is this project's own domain
vocabulary. Renaming BigQuery's concept in this adapter (`schema_id`, or
similar) would avoid the collision but make this code harder to match
against BigQuery's own documentation, where every example calls it
`dataset`. Keeping BigQuery's name and writing the collision down
explicitly, in the constructor's own docstring, was judged better than
either silently living with the ambiguity or hiding it behind a
different word.

## Why a failed insert does not raise on its own, unlike every other adapter so far

```python
errors = self._client.insert_rows_json(table_id, list(rows))

if errors:
    raise RuntimeError(
        f"BigQuery rejected some rows when inserting into {table_id}: {errors}"
    )
```

Every adapter written before this one raises when something goes wrong:
a missing file, a missing key, an insert failing on the Postgres
connection. BigQuery's `insert_rows_json` does not follow that pattern,
it returns a list, empty on full success, containing one entry per
rejected row (with BigQuery's own explanation) when some rows failed to
insert while others succeeded. That is a deliberate design choice on
BigQuery's part: a partial failure across a batch of rows is a normal,
expected outcome for that call, not treated as exceptional the way a
failed database transaction is.

Left unchecked, that returned list would just sit there unused, and
`save` would look like it completed successfully even if BigQuery
rejected every row in the batch. For a project whose entire purpose is
catching bad data before it gets used, silently swallowing a rejection
like that would undermine the point of the whole pipeline. This adapter
checks the list itself and raises a `RuntimeError` carrying BigQuery's
own error details when it is not empty, translating BigQuery's
return-errors-as-data convention into the same raise-on-failure behavior
every other adapter already has, so a caller does not need to know which
adapter it is talking to in order to notice a failure.

## Why the raised error includes BigQuery's own error detail, not a generic message

```python
raise RuntimeError(
    f"BigQuery rejected some rows when inserting into {table_id}: {errors}"
)
```

`test_save_raises_when_bigquery_returns_row_errors` checks the message
contains both the table id and the specific reason BigQuery gave for
rejecting a row. A bare `raise RuntimeError("insert failed")` would
technically satisfy "this adapter raises on failure", but it would throw
away the one piece of information that actually explains what went
wrong, forcing whoever catches it to go dig through BigQuery's own logs
to find out what this project already had in hand at the moment it
failed.

## Same duck-typing and extras pattern as every adapter before it

`BigqueryDatasetRepository` does not import `google-cloud-bigquery`, it
only calls `.insert_rows_json` on whatever `client` object it is given,
same reasoning as `PostgresDatasetRepository` and every storage adapter
before it: testable with a fake, no real GCP project needed to run these
tests. `google-cloud-bigquery` gets its own `bigquery` extra in
`pyproject.toml`, following `sklearn`, `postgres`, `gcs`, and `s3`.
