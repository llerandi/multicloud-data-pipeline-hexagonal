# 10 · PostgresDatasetRepository adapter

Branch: `feature/postgres-repository-adapter` · Technical write-up:
[docs/10-postgres-repository-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/10-postgres-repository-adapter.md)

## The concept this stage teaches

This adapter never imports `psycopg`. It's written against DB-API 2.0 -
the shape every Python database driver shares (`.cursor()`, `.commit()`,
`.execute()`/`.executemany()`) - instead of against one specific library.
That's a stronger form of the idea `LocalFileStorage` introduced in
[05](05-·-LocalFileStorage-adapter): depend on the minimum shape actually
needed, not the concrete thing that happens to provide it today.

## What to notice

- Row *values* go through `%s` placeholders (the driver escapes them
  safely); table and column *names* can't - no driver lets you bind an
  identifier as a query parameter. `_quote_identifier` handles that
  second category by hand. Two different categories of untrusted string,
  two deliberately different defenses.
- The constructor takes an already-open `connection`, not a connection
  string - same pattern as `LocalFileStorage` taking a resolved
  `root_dir` and `SklearnModelInference` taking an already-fitted model:
  the adapter is handed a ready collaborator, it doesn't know how to
  build one.
- An empty list of rows is a no-op, not an error (nothing to infer
  columns from) - the same choice `DataQualityReport.null_ratio` made for
  an empty dataset back in [01](01-·-Domain-model). A missing column in a
  later row raises a plain `KeyError`, not a custom exception.
- Every test uses `FakeConnection`/`FakeCursor` - no real Postgres
  needed. What's *not* tested yet: a real database. That's tracked in
  [Roadmap](Roadmap-and-status), not silently skipped.

## Why it matters for the rest of the project

"Depend on the protocol, not the library" is the same move
[11](11-·-GcsFileStorage-adapter) and [12](12-·-S3FileStorage-adapter)
make for storage, and [13](13-·-BigqueryDatasetRepository-adapter) makes
for the second `DatasetRepository` adapter - each one testable without
installing or authenticating against the real cloud service.

Back to [Home](Home) · Previous: [09 · SklearnModelInference adapter](09-·-SklearnModelInference-adapter) · Next: [11 · GcsFileStorage adapter](11-·-GcsFileStorage-adapter)
