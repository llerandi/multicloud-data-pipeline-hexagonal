# Roadmap and status

Mirrors the "Current status" checklist in the
[README](https://github.com/llerandi/multicloud-data-pipeline-hexagonal#current-status),
with room for the *why* behind what's still pending. See [Home](Home) for
the full learning path.

## Done

- Domain layer: `DataQualityReport`, `QualityThresholds`,
  `DatasetRejectedError`, the null-ratio rule. ([01](01-·-Domain-model))
- Tooling: `pyproject.toml`, GitHub Actions CI (lint + tests per PR).
  ([02](02-·-Tooling))
- Application ports: `FileStorage`, `DatasetRepository`, `MetricsPublisher`,
  `NotificationPort`. ([03](03-·-Application-ports))
- `ValidateAndIngestDataset` use case, wired to all four ports.
  ([04](04-·-ValidateAndIngestDataset-use-case))
- `FileStorage`: `LocalFileStorage` ([05](05-·-LocalFileStorage-adapter)),
  `GcsFileStorage` ([11](11-·-GcsFileStorage-adapter)), `S3FileStorage`
  ([12](12-·-S3FileStorage-adapter)) - all three cloud-storage adapters
  the scope asked for.
- `MetricsPublisher`: `ConsoleMetricsPublisher`
  ([06](06-·-ConsoleMetricsPublisher-adapter)),
  `CloudMonitoringMetricsPublisher`
  ([14](14-·-CloudMonitoringMetricsPublisher-adapter)) - publishes a
  plain-dict "point" shape, real `TimeSeries` translation still open, see
  below.
- `NotificationPort`: `LogStubNotificationPort` - dev/test only.
  ([07](07-·-LogStubNotificationPort-adapter))
- `DatasetRepository`: `PostgresDatasetRepository`
  ([10](10-·-PostgresDatasetRepository-adapter)), unit tested with a fake
  connection, real database integration test still pending;
  `BigqueryDatasetRepository`
  ([13](13-·-BigqueryDatasetRepository-adapter)).
- `ModelInferencePort`: contract defined
  ([08](08-·-ModelInferencePort)), local scikit-learn adapter built
  ([09](09-·-SklearnModelInference-adapter)).

## Pending

- `NotificationPort`: Slack/email adapter - the only port from stage 03
  still without a real adapter.
- `ModelInferencePort`: Vertex AI adapter.
- `PostgresDatasetRepository`: a real, running-database integration test
  (currently unit tested against a fake connection only) - most likely
  via a Postgres service container in CI.
- `CloudMonitoringMetricsPublisher`: translating the adapter's plain-dict
  "point" shape into real `TimeSeries`/`Point`/`MonitoredResource`
  protobuf objects and calling `create_time_series` - deliberately left
  to a client wrapper that doesn't exist yet. ([14](14-·-CloudMonitoringMetricsPublisher-adapter))
- `FileStorage` adapters don't agree on a not-found exception type yet:
  `FileNotFoundError` (local), `google.cloud.exceptions.NotFound` (GCS),
  `botocore.exceptions.ClientError` (S3) - documented as a real,
  unresolved inconsistency, not silently accepted.
  ([11](11-·-GcsFileStorage-adapter), [12](12-·-S3FileStorage-adapter))
- `out_of_range_count` in the quality report - still hardcoded to `0`
  because there's no schema representation yet to define what "in range"
  means per column ([04](04-·-ValidateAndIngestDataset-use-case)).
- Wiring `predict` (ModelInferencePort) into the use case - deferred until
  it's actually needed by a caller.
- End-to-end runnable pipeline command - the individual adapters exist
  now, but nothing yet composes them into one runnable entry point.

## Decisions worth revisiting later

- `MetricsPublisher`'s console adapter uses `print`; `NotificationPort`'s
  stub uses `logging`, deliberately different for now
  ([07](07-·-LogStubNotificationPort-adapter)). Worth checking whether
  that still makes sense now that `CloudMonitoringMetricsPublisher`
  exists.
- Null detection treats `None` and `""` as null but not `0`/`False`
  ([04](04-·-ValidateAndIngestDataset-use-case)) - revisit if a dataset
  ever needs a different null convention.
- The three `FileStorage` adapters raise three different exceptions for
  "not found" - see Pending above. Worth deciding on a normalized
  exception once a fourth adapter or a real caller actually needs to
  catch it uniformly.
