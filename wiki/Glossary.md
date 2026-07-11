# Glossary

Defined against this project's actual code, not in the abstract. See
[Home](Home) for the full learning path.

**Domain layer** - the innermost layer (`src/domain/`). Imports nothing
outside the Python standard library: no pandas, no cloud SDK, no database
driver. Holds the business rule ("reject a dataset with more than 5% null
values") as plain Python, so it's testable without running any
infrastructure. See [01 · Domain model](01-Domain-Model).

**Application layer** - (`src/application/`). Knows the *steps* of the
pipeline (read, validate, persist, notify, infer) but not which cloud
provider runs them. Depends on the domain layer and defines the ports it
needs from the outside world. See [03 · Application ports](03-Application-Ports)
and [04 · Use case](04-Validate-And-Ingest-Use-Case).

**Infrastructure layer** - (`src/infrastructure/`). Implements each port for
a specific provider (GCS, S3, BigQuery, console, log stub...). This is
where actual cloud SDK calls live. See [05](05-Local-Filesystem-Adapter),
[06](06-Console-Metrics-Publisher), [07](07-Log-Stub-Notification-Port).

**Port** - an abstract contract (`abc.ABC` + `@abstractmethod`) that says
"I need something that can do X" without saying which concrete thing
provides it. Defined in `application/ports/`. Example: `FileStorage` says
"something that can `read(path)`", without knowing if that's local disk,
GCS, or S3. Python enforces the contract at runtime - a subclass that
forgets to implement a method can't be instantiated. See
[03 · Application ports](03-Application-Ports).

**Adapter** - a concrete class that implements a port for one specific
technology. `LocalFileStorage` and (eventually) `GCSFileStorage` are both
adapters for the `FileStorage` port. The application layer can swap one for
the other without changing any of its own code. See
[05 · LocalFileStorage adapter](05-Local-Filesystem-Adapter).

**Use case** - one orchestration flow, one class, one job
(`ValidateAndIngestDataset`). Receives its ports via the constructor
(dependency injection) instead of constructing its own GCS or BigQuery
clients. This is what makes it testable with in-memory fakes and portable
across cloud providers without modification. See
[04 · Use case](04-Validate-And-Ingest-Use-Case).

**Value object** - an object with no identity: two instances with the same
field values are simply equal and interchangeable (`DataQualityReport`).
Contrast with an *entity*, which keeps its identity even as its data
changes (a customer row is "the same customer" after an address update).
`@dataclass(frozen=True)` is the mechanism used here. See
[01 · Domain model](01-Domain-Model).

**Dependency injection** - passing a class's dependencies in from outside
(as constructor arguments) instead of the class creating them itself. It's
what lets `ValidateAndIngestDataset` run against fake ports in tests and
real cloud adapters in production, with zero code changes to the use case
itself. See [04 · Use case](04-Validate-And-Ingest-Use-Case).

**Dependency direction** - the rule that infrastructure depends on
application, application depends on domain, and domain depends on nothing.
Dependencies only ever point inward. This is the actual definition of
"hexagonal": not the hexagon shape, but this one-way arrow.
