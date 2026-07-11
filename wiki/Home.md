# Multicloud Data Pipeline Hexagonal — Wiki

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
| 1 | The domain layer knows nothing about the outside world | [01 · Domain model](01-Domain-Model) | [docs/01-domain-model.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/01-domain-model.md) |
| 2 | Project tooling as scaffolding, not architecture | [02 · Tooling](02-Tooling) | [docs/02-tooling.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/02-tooling.md) |
| 3 | Ports: contracts the application layer depends on | [03 · Application ports](03-Application-Ports) | [docs/03-application-ports.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/03-application-ports.md) |
| 4 | The use case: orchestration without knowing the cloud | [04 · ValidateAndIngestDataset use case](04-Validate-And-Ingest-Use-Case) | [docs/04-validate-and-ingest-use-case.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/04-validate-and-ingest-use-case.md) |
| 5 | The first adapter: proving a port can be implemented | [05 · LocalFileStorage adapter](05-Local-Filesystem-Adapter) | [docs/05-local-filesystem-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/05-local-filesystem-adapter.md) |
| 6 | A second adapter for the same use case, no changes to it | [06 · ConsoleMetricsPublisher adapter](06-Console-Metrics-Publisher) | [docs/06-console-metrics-publisher.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/06-console-metrics-publisher.md) |
| 7 | Adapters for the same port can behave differently on purpose | [07 · LogStubNotificationPort adapter](07-Log-Stub-Notification-Port) | [docs/07-log-stub-notification-port.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/07-log-stub-notification-port.md) |
| 8 | An optional port: architecture expressing "only sometimes" | [08 · ModelInferencePort](08-Model-Inference-Port) | [docs/08-model-inference-port.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/08-model-inference-port.md) |

Also in this Wiki:

- [Glossary](Glossary) - domain, port, adapter, use case, value object, dependency injection, defined against this project's own code.
- [Roadmap and status](Roadmap) - what's built, what's pending, and decisions worth revisiting later.

## How to read this project

1. Read the [README](https://github.com/llerandi/multicloud-data-pipeline-hexagonal#readme) for scope and architecture overview.
2. Go stage by stage through the table above, in order - each one assumes the previous ones already happened.
3. For each stage, read the Wiki page first (the concept), then the `docs/` write-up (the implementation), then the actual PR diff on GitHub if you want to see the real code changes.
