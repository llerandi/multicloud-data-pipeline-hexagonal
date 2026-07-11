# Roadmap and status

Mirrors the "Current status" checklist in the
[README](https://github.com/llerandi/multicloud-data-pipeline-hexagonal#current-status),
with room for the *why* behind what's still pending. See [Home](Home) for
the full learning path.

## Done

- Domain layer: `DataQualityReport`, `QualityThresholds`,
  `DatasetRejectedError`, the null-ratio rule. ([01](01-Domain-Model))
- Tooling: `pyproject.toml`, GitHub Actions CI (lint + tests per PR).
  ([02](02-Tooling))
- Application ports: `FileStorage`, `DatasetRepository`, `MetricsPublisher`,
  `NotificationPort`. ([03](03-Application-Ports))
- `ValidateAndIngestDataset` use case, wired to all four ports.
  ([04](04-Validate-And-Ingest-Use-Case))
- `LocalFileStorage` adapter - dev/test only, first proof a port can be
  implemented and actually run end to end. ([05](05-Local-Filesystem-Adapter))
- `ConsoleMetricsPublisher` adapter - dev only, prints metrics to stdout.
  ([06](06-Console-Metrics-Publisher))
- `LogStubNotificationPort` adapter - dev/test only, logs instead of
  paging Slack/email. ([07](07-Log-Stub-Notification-Port))
- `ModelInferencePort` - contract defined, no adapter yet.
  ([08](08-Model-Inference-Port))

## Pending

- `FileStorage`: GCS, S3 adapters - the actual multicloud proof.
- `DatasetRepository`: BigQuery, Postgres adapters.
- `MetricsPublisher`: Cloud Monitoring adapter.
- `NotificationPort`: Slack/email adapter.
- `ModelInferencePort`: local scikit-learn adapter, then Vertex AI adapter.
- `out_of_range_count` in the quality report - currently hardcoded to `0`
  because there's no schema representation yet to define what "in range"
  means per column ([04](04-Validate-And-Ingest-Use-Case)).
- Wiring `predict` (ModelInferencePort) into the use case - deferred until
  at least one real adapter exists to call it with.
- End-to-end runnable pipeline - blocked on the first real infrastructure
  adapter landing; today only the domain and application layers exist with
  no cloud adapter wired in.

## Decisions worth revisiting later

Space for things that were reasonable calls at this stage but might not
hold once more adapters exist - update as the project grows:

- `MetricsPublisher`'s console adapter uses `print`; `NotificationPort`'s
  stub uses `logging`, deliberately different for now
  ([07](07-Log-Stub-Notification-Port)). Worth checking whether that still
  makes sense once a real Cloud Monitoring adapter exists.
- Null detection treats `None` and `""` as null but not `0`/`False`
  ([04](04-Validate-And-Ingest-Use-Case)) - revisit if a dataset ever needs
  a different null convention.
