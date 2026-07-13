# PR summaries

Each file in this folder documents one pull request: what changed, and more
importantly, why it was built that way. The code itself stays free of this
level of explanation (docstrings cover the short version), this is the long
version, for whoever wants to understand the reasoning later, including
future you.

Read them in order, each one assumes the previous ones already happened.

1. [Domain model](01-domain-model.md) — `feature/domain-model`
2. [Tooling](02-tooling.md) — `chore/tooling`
3. [Application ports](03-application-ports.md) — `feature/application-ports`
4. [ValidateAndIngestDataset use case](04-validate-and-ingest-use-case.md) — `feature/validate-and-ingest-use-case`
5. [LocalFileStorage adapter](05-local-filesystem-adapter.md) — `feature/local-filesystem-adapter`
6. [ConsoleMetricsPublisher adapter](06-console-metrics-publisher.md) — `feature/console-metrics-publisher`
7. [LogStubNotificationPort adapter](07-log-stub-notification-port.md) — `feature/log-stub-notification-port`
8. [ModelInferencePort](08-model-inference-port.md) — `feature/model-inference-port`
9. [SklearnModelInference adapter](09-sklearn-inference-adapter.md) — `feature/sklearn-inference-adapter`
10. [PostgresDatasetRepository adapter](10-postgres-repository-adapter.md) — `feature/postgres-repository-adapter`
