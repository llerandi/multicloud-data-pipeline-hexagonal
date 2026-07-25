# 13 · BigqueryDatasetRepository adapter

Branch: `feature/bigquery-repository-adapter` · Technical write-up:
[docs/13-bigquery-repository-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/13-bigquery-repository-adapter.md)

## The concept this stage teaches

`DatasetRepository` now has both adapters the project scope asked for.
Where [12](12-·-S3FileStorage-adapter) showed two SDKs shaped differently
but agreeing on "raise on failure", this stage shows a real API that
doesn't raise at all by convention. BigQuery's `insert_rows_json` returns
a list - empty on full success, one entry per rejected row on partial
failure - rather than throwing. For a pipeline whose whole purpose is
catching bad data, silently letting that list sit unused would undermine
the project's own premise. The adapter checks it and raises a
`RuntimeError` itself, translating BigQuery's return-errors-as-data
convention into the same raise-on-failure contract every other adapter
already honors - so a caller never needs to know which adapter it's
talking to in order to notice a failure.

## What to notice

- The raised error includes BigQuery's own error detail, not a generic
  message - a bare `RuntimeError("insert failed")` would technically
  satisfy "raises on failure" but throw away the one piece of
  information that explains *why*, forcing whoever catches it to go dig
  through BigQuery's logs for something this adapter already had in hand.
- A direct naming collision is called out explicitly in the docstring:
  BigQuery's own "dataset" (a namespace of tables) versus this project's
  "dataset" (the CSV/JSON file being validated) - same English word, two
  unrelated meanings. Kept as BigQuery's own name rather than renamed,
  so the code still matches BigQuery's documentation, with the collision
  documented rather than hidden.
- Same duck-typing and extras pattern as every adapter before it - no
  `google-cloud-bigquery` import, its own `bigquery` extra.

## Why it matters for the rest of the project

This is the last adapter that fits the "call one real method on an
injected client" pattern established since
[09](09-·-SklearnModelInference-adapter). [14](14-·-CloudMonitoringMetricsPublisher-adapter)
is where that pattern runs out.

Back to [Home](Home) · Previous: [12 · S3FileStorage adapter](12-·-S3FileStorage-adapter) · Next: [14 · CloudMonitoringMetricsPublisher adapter](14-·-CloudMonitoringMetricsPublisher-adapter)
