# 03 · Application ports

Branch: `feature/application-ports` · Technical write-up:
[docs/03-application-ports.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/03-application-ports.md)

## The concept this stage teaches

This is the "ports" half of "ports and adapters", and arguably the single
most important stage for understanding the whole architecture. A **port**
is a contract - "I need something that can `read(path)`" - with no
statement of *how*. `FileStorage`, `DatasetRepository`, `MetricsPublisher`
and `NotificationPort` are all defined here as `abc.ABC` classes with
`@abstractmethod`s and zero implementation. The concrete "how" (GCS
adapter, S3 adapter, BigQuery adapter...) is deliberately written later,
in a different layer, against this same contract.

## What to notice

- Python's `abc` enforces the contract *at runtime*: an incomplete
  subclass fails with `TypeError` the moment it's instantiated, not later
  when some missing method finally gets called in production.
- Type hints favor the least specific type that still works
  (`Sequence[Mapping[str, Any]]` instead of `list[dict]`) - depend on the
  minimum shape actually needed, same idea as depending on an interface
  instead of a concrete class.
- `MetricsPublisher` is the only port that imports a domain type
  (`DataQualityReport`) - because it's the only one whose whole job is to
  publish that specific object's fields.
- Each port's tests build a minimal real subclass instead of a mock - this
  means a typo'd method name fails to even import, which a generic
  `Mock()` would silently accept.

## Why it matters for the rest of the project

Every adapter written from here on (stages 05, 06, 07, and eventually GCS,
S3, BigQuery, Slack, Vertex AI) is judged against these four contracts.
The use case in the next stage is only possible because these ports exist
first - it can be written and tested before a single real adapter does.

Back to [Home](Home) · Previous: [02 · Tooling](02-Tooling) · Next: [04 · Use case](04-Validate-And-Ingest-Use-Case)
