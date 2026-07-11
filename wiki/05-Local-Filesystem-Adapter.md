# 05 · LocalFileStorage adapter

Branch: `feature/local-filesystem-adapter` · Technical write-up:
[docs/05-local-filesystem-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/05-local-filesystem-adapter.md)

## The concept this stage teaches

The "adapters" half of "ports and adapters" arrives here: the first class
in the project that *implements* a port instead of just defining one.
`LocalFileStorage` backs `FileStorage` with the local disk. It's not meant
for production - its job is to prove the shape works end to end, and to
give the GCS and S3 adapters (once written) something concrete to be
compared against: same three methods on the same port, different place
the bytes come from.

## What to notice

- `root_dir` is a constructor argument, `read(path)` only takes the
  relative key - matching the shape a GCS/S3 adapter will need (bucket
  name fixed at construction, key passed per call). This is what lets the
  application layer call `file_storage.read(path)` without caring which
  adapter is behind it.
- A missing file raises the standard `FileNotFoundError`, unwrapped -
  wrapping it in a custom exception here would hide a clear error behind
  a new type, not add information.
- The integration test (`tests/integration/test_local_pipeline.py`) is the
  first test where *one* dependency is real (`LocalFileStorage`) while the
  other three are still fakes - unit tests prove each class works alone,
  this proves they work wired together, which neither unit suite can
  catch on its own.

## Why it matters for the rest of the project

This stage is the template. Every real cloud adapter that follows (GCS,
S3, BigQuery, Postgres, Slack, Vertex AI) is judged against the same bar:
implement the port's contract, and prove it with the same two kinds of
test - isolated unit tests, plus at least one integration test wiring it
into the actual use case.

Back to [Home](Home) · Previous: [04 · Use case](04-Validate-And-Ingest-Use-Case) · Next: [06 · ConsoleMetricsPublisher adapter](06-Console-Metrics-Publisher)
