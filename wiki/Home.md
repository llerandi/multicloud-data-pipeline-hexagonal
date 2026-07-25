# Multicloud Data Pipeline Hexagonal - Wiki

This is a learning project: it exists to practice **hexagonal architecture**
(ports and adapters) applied to a real-ish data engineering problem. The code
favors clarity over brevity on purpose.

This Wiki is the conceptual thread that ties the project together. For each
pull request, [`docs/`](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/tree/main/docs)
in the repo explains **what changed and why, at code level**. This Wiki
explains **what hexagonal-architecture idea that PR is teaching**, so someone
following the project stage by stage can use it as a course, not just a
changelog.

Read `docs/` and the matching Wiki page together - `docs/` is the technical
write-up, the Wiki page is the "why this matters for the architecture" framing.

## Learning path

| Stage | Concept | Wiki page | Technical write-up (docs/) |
|---|---|---|---|
| 1 | The domain layer knows nothing about the outside world | [01 · Domain model](01-·-Domain-model) | [docs/01-domain-model.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/01-domain-model.md) |
| 2 | Project tooling as scaffolding, not architecture | [02 · Tooling](02-·-Tooling) | [docs/02-tooling.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/02-tooling.md) |
| 3 | Ports: contracts the application layer depends on | [03 · Application ports](03-·-Application-ports) | [docs/03-application-ports.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/03-application-ports.md) |
| 4 | The use case: orchestration without knowing the cloud | [04 · ValidateAndIngestDataset use case](04-·-ValidateAndIngestDataset-use-case) | [docs/04-validate-and-ingest-use-case.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/04-validate-and-ingest-use-case.md) |
| 5 | The first adapter: proving a port can be implemented | [05 · LocalFileStorage adapter](05-·-LocalFileStorage-adapter) | [docs/05-local-filesystem-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/05-local-filesystem-adapter.md) |
| 6 | A second adapter for the same use case, no changes to it | [06 · ConsoleMetricsPublisher adapter](06-·-ConsoleMetricsPublisher-adapter) | [docs/06-console-metrics-publisher.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/06-console-metrics-publisher.md) |
| 7 | Adapters for the same port can behave differently on purpose | [07 · LogStubNotificationPort adapter](07-·-LogStubNotificationPort-adapter) | [docs/07-log-stub-notification-port.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/07-log-stub-notification-port.md) |
| 8 | An optional port: architecture expressing "only sometimes" | [08 · ModelInferencePort](08-·-ModelInferencePort) | [docs/08-model-inference-port.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/08-model-inference-port.md) |
| 9 | Wrapping a real library behind a port: narrow adapter, isolated dependency | [09 · SklearnModelInference adapter](09-·-SklearnModelInference-adapter) | [docs/09-sklearn-inference-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/09-sklearn-inference-adapter.md) |
| 10 | Duck-typing a protocol (DB-API 2.0) instead of importing a driver | [10 · PostgresDatasetRepository adapter](10-·-PostgresDatasetRepository-adapter) | [docs/10-postgres-repository-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/10-postgres-repository-adapter.md) |
| 11 | A real cloud adapter, same `path` contract as the local one | [11 · GcsFileStorage adapter](11-·-GcsFileStorage-adapter) | [docs/11-gcs-file-storage-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/11-gcs-file-storage-adapter.md) |
| 12 | The "swap providers" claim made concrete: two SDKs, one contract | [12 · S3FileStorage adapter](12-·-S3FileStorage-adapter) | [docs/12-s3-file-storage-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/12-s3-file-storage-adapter.md) |
| 13 | Normalizing a return-errors-as-data API into raise-on-failure | [13 · BigqueryDatasetRepository adapter](13-·-BigqueryDatasetRepository-adapter) | [docs/13-bigquery-repository-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/13-bigquery-repository-adapter.md) |
| 14 | When duck-typing one method isn't enough: inventing your own shape | [14 · CloudMonitoringMetricsPublisher adapter](14-·-CloudMonitoringMetricsPublisher-adapter) | [docs/14-cloud-monitoring-metrics-publisher.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/14-cloud-monitoring-metrics-publisher.md) |
| 15 | Confirming stage 14 was the exception, not the new rule | [15 · SlackNotificationPort adapter](15-·-SlackNotificationPort-adapter) | [docs/15-slack-notification-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/15-slack-notification-adapter.md) |
| 16 | The second "two adapters, one port" comparison: position vs. naming | [16 · VertexAiModelInference adapter](16-·-VertexAiModelInference-adapter) | [docs/16-vertex-ai-inference-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/16-vertex-ai-inference-adapter.md) |

Also in this Wiki:

- [Glossary](Glossary) - domain, port, adapter, use case, value object, dependency injection, defined against this project's own code.
- [Roadmap and status](Roadmap-and-status) - what's built, what's pending, and decisions worth revisiting later.

## How to read this project

1. Read the [README](https://github.com/llerandi/multicloud-data-pipeline-hexagonal#readme) for scope and architecture overview.
2. Go stage by stage through the table above, in order - each one assumes the previous ones already happened.
3. For each stage, read the Wiki page first (the concept), then the `docs/` write-up (the implementation), then the actual PR diff on GitHub if you want to see the real code changes.

## Where the project stands

As of stage 16, every port defined in [03 · Application ports](03-·-Application-ports)
has every adapter its original scope called for: `FileStorage` (local,
GCS, S3), `DatasetRepository` (Postgres, BigQuery), `MetricsPublisher`
(console, Cloud Monitoring), `NotificationPort` (log stub, Slack), and
`ModelInferencePort` (scikit-learn, Vertex AI). See
[Roadmap and status](Roadmap-and-status) for what's still genuinely open
(a composition root, a couple of documented gaps) versus what's done.

Three arcs worth reading back to back for the contrast they set up:

- Stages 9-13: five adapters, all built by duck-typing one plain method
  on an injected client, no SDK import required.
- Stage 14: the pattern runs out - Cloud Monitoring has no single plain
  call to duck-type, so the adapter invents its own shape instead.
- Stage 15: back to duck-typing, confirming 14 was the exception.
- Stages 11-12 and 8-9-16: two pairs of "same port, two adapters, put
  side by side on purpose" - one comparing client shapes (`FileStorage`),
  one comparing data shapes (`ModelInferencePort`).
