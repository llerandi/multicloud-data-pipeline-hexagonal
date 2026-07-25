# Roadmap and status

Mirrors the "Current status" checklist in the
[README](https://github.com/llerandi/multicloud-data-pipeline-hexagonal#current-status),
with room for the *why* behind what's still pending. See [Home](Home) for
the full learning path.

As of stage 16, every port defined in
[03 · Application ports](03-·-Application-ports) has every adapter its
original scope called for. What's left is genuinely open work, not
missing scope - listed below.

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
  ([12](12-·-S3FileStorage-adapter)) - all three, complete.
- `MetricsPublisher`: `ConsoleMetricsPublisher`
  ([06](06-·-ConsoleMetricsPublisher-adapter)),
  `CloudMonitoringMetricsPublisher`
  ([14](14-·-CloudMonitoringMetricsPublisher-adapter)) - both, complete;
  Cloud Monitoring publishes a plain-dict "point" shape, real `TimeSeries`
  translation still open, see below.
- `NotificationPort`: `LogStubNotificationPort`
  ([07](07-·-LogStubNotificationPort-adapter)), `SlackNotificationPort`
  ([15](15-·-SlackNotificationPort-adapter)) - both, complete.
- `DatasetRepository`: `PostgresDatasetRepository`
  ([10](10-·-PostgresDatasetRepository-adapter)), unit tested with a fake
  connection, real database integration test still pending;
  `BigqueryDatasetRepository`
  ([13](13-·-BigqueryDatasetRepository-adapter)) - both, complete.
- `ModelInferencePort`: contract defined
  ([08](08-·-ModelInferencePort)), `SklearnModelInference`
  ([09](09-·-SklearnModelInference-adapter)), `VertexAiModelInference`
  ([16](16-·-VertexAiModelInference-adapter)) - both, complete.

## Pending

- A composition root - a script or entry point that builds real clients
  (a GCS bucket, a Postgres connection, a Vertex AI endpoint, ...) and
  wires them into `ValidateAndIngestDataset` for an actual end-to-end
  run. Every adapter now exists; nothing yet assembles them into a
  runnable pipeline.
- `PostgresDatasetRepository`: a real, running-database integration test
  (currently unit tested against a fake connection only) - most likely
  via a Postgres service container in CI.
  ([10](10-·-PostgresDatasetRepository-adapter))
- `CloudMonitoringMetricsPublisher`: translating the adapter's plain-dict
  "point" shape into real `TimeSeries`/`Point`/`MonitoredResource`
  protobuf objects and calling `create_time_series` - deliberately left
  to a client wrapper that doesn't exist yet.
  ([14](14-·-CloudMonitoringMetricsPublisher-adapter))
- `FileStorage` adapters don't agree on a not-found exception type yet:
  `FileNotFoundError` (local), `google.cloud.exceptions.NotFound` (GCS),
  `botocore.exceptions.ClientError` (S3) - documented as a real,
  unresolved inconsistency, not silently accepted.
  ([11](11-·-GcsFileStorage-adapter), [12](12-·-S3FileStorage-adapter))
- `out_of_range_count` in the quality report - still hardcoded to `0`
  because there's no schema representation yet to define what "in range"
  means per column. ([04](04-·-ValidateAndIngestDataset-use-case))
- Wiring `predict` (ModelInferencePort) into the use case - deferred until
  it's actually needed by a caller, now that a real adapter exists to
  call it with.

## Decisions worth revisiting later

- `MetricsPublisher`'s console adapter uses `print`; `NotificationPort`'s
  log stub uses `logging`, deliberately different
  ([07](07-·-LogStubNotificationPort-adapter)). Worth checking whether
  that still makes sense now that both ports have real cloud adapters too.
- Null detection treats `None` and `""` as null but not `0`/`False`
  ([04](04-·-ValidateAndIngestDataset-use-case)) - revisit if a dataset
  ever needs a different null convention.
- The three `FileStorage` adapters raise three different exceptions for
  "not found" - see Pending above. Worth deciding on a normalized
  exception now that a composition root is the next real piece of work
  and will need to catch these uniformly.
