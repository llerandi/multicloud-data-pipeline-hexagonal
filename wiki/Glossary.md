# Glossary

Defined against this project's actual code, not in the abstract. See
[Home](Home) for the full learning path.

**Domain layer** - the innermost layer (`src/domain/`). Imports nothing
outside the Python standard library: no pandas, no cloud SDK, no database
driver. Holds the business rule ("reject a dataset with more than 5% null
values") as plain Python, so it's testable without running any
infrastructure. See [01 · Domain model](01-·-Domain-model).

**Application layer** - (`src/application/`). Knows the *steps* of the
pipeline (read, validate, persist, notify, infer) but not which cloud
provider runs them. Depends on the domain layer and defines the ports it
needs from the outside world. See [03 · Application ports](03-·-Application-ports)
and [04 · Use case](04-·-ValidateAndIngestDataset-use-case).

**Infrastructure layer** - (`src/infrastructure/`). Implements each port for
a specific provider (GCS, S3, BigQuery, Postgres, Cloud Monitoring,
console, log stub, scikit-learn...). This is where actual cloud SDK calls
live. See stages [05](05-·-LocalFileStorage-adapter) through
[14](14-·-CloudMonitoringMetricsPublisher-adapter).

**Port** - an abstract contract (`abc.ABC` + `@abstractmethod`) that says
"I need something that can do X" without saying which concrete thing
provides it. Defined in `application/ports/`. Example: `FileStorage` says
"something that can `read(path)`", without knowing if that's local disk,
GCS, or S3. Python enforces the contract at runtime - a subclass that
forgets to implement a method can't be instantiated. See
[03 · Application ports](03-·-Application-ports).

**Adapter** - a concrete class that implements a port for one specific
technology. `LocalFileStorage` and `GcsFileStorage` are both adapters for
the `FileStorage` port. The application layer can swap one for the other
without changing any of its own code. See
[05 · LocalFileStorage adapter](05-·-LocalFileStorage-adapter).

**Duck typing against a real SDK** - the recurring technique behind every
adapter from [09](09-·-SklearnModelInference-adapter) through
[13](13-·-BigqueryDatasetRepository-adapter): the adapter is constructed
with an already-built, already-authenticated collaborator (a connection,
a bucket, a client) and only calls the one or two plain methods it needs
on it - `.cursor().executemany()`, `.blob(path).download_as_bytes()`,
`.insert_rows_json()` - without ever importing the real SDK that defines
those classes. This is what lets each adapter be unit tested with a small
fake standing in for the real object, no real cloud account needed. It
breaks down when the real API has no single plain-argument call to
duck-type - see [14 · CloudMonitoringMetricsPublisher](14-·-CloudMonitoringMetricsPublisher-adapter),
which has to invent its own shape instead.

**Optional dependency extra** - a named group in `pyproject.toml`'s
`[project.optional-dependencies]` (`sklearn`, `postgres`, `gcs`, `s3`,
`bigquery`, `monitoring`) that isolates one adapter's real dependency from
every other one. `pip install -e ".[dev]"` stays light for anyone not
touching that adapter; `pip install -e ".[dev,sklearn]"` opts in only when
needed. Started in [09 · SklearnModelInference adapter](09-·-SklearnModelInference-adapter),
reused by every real adapter since.

**Use case** - one orchestration flow, one class, one job
(`ValidateAndIngestDataset`). Receives its ports via the constructor
(dependency injection) instead of constructing its own GCS or BigQuery
clients. This is what makes it testable with in-memory fakes and portable
across cloud providers without modification. See
[04 · Use case](04-·-ValidateAndIngestDataset-use-case).

**Value object** - an object with no identity: two instances with the same
field values are simply equal and interchangeable (`DataQualityReport`).
Contrast with an *entity*, which keeps its identity even as its data
changes (a customer row is "the same customer" after an address update).
`@dataclass(frozen=True)` is the mechanism used here. See
[01 · Domain model](01-·-Domain-model).

**Dependency injection** - passing a class's dependencies in from outside
(as constructor arguments) instead of the class creating them itself. It's
what lets `ValidateAndIngestDataset` run against fake ports in tests and
real cloud adapters in production, with zero code changes to the use case
itself. See [04 · Use case](04-·-ValidateAndIngestDataset-use-case).

**Dependency direction** - the rule that infrastructure depends on
application, application depends on domain, and domain depends on nothing.
Dependencies only ever point inward. This is the actual definition of
"hexagonal": not the hexagon shape, but this one-way arrow.
