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

Also in this Wiki:

- [Glossary](Glossary) - domain, port, adapter, use case, value object, dependency injection, defined against this project's own code.
- [Roadmap and status](Roadmap-and-status) - what's built, what's pending, and decisions worth revisiting later.

## How to read this project

1. Read the [README](https://github.com/llerandi/multicloud-data-pipeline-hexagonal#readme) for scope and architecture overview.
2. Go stage by stage through the table above, in order - each one assumes the previous ones already happened.
3. For each stage, read the Wiki page first (the concept), then the `docs/` write-up (the implementation), then the actual PR diff on GitHub if you want to see the real code changes.

## Two arcs so far

Stages 1–8 build the domain, the ports, and the use case, then prove one
port (`FileStorage`) can be implemented at all with `LocalFileStorage`.
Stages 9–14 are all real adapters against real cloud SDKs - and they trace
their own arc: 9 through 13 all work by duck-typing one plain method on an
injected client, never importing the SDK itself; 14 is where that pattern
runs out and the adapter has to invent its own translation shape instead.
Worth reading 9–14 back to back for that contrast.
