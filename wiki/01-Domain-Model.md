# 01 · Domain model

Branch: `feature/domain-model` · Technical write-up:
[docs/01-domain-model.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/01-domain-model.md)

## The concept this stage teaches

The innermost ring of hexagonal architecture is the **domain**, and the
defining test of "is this really domain code" is: *could this class exist
if GCS, S3, and BigQuery had never been invented?* `src/domain/` imports
nothing outside the Python standard library on purpose - no cloud SDK, no
database driver, not even pandas. That constraint is not about minimalism,
it's what makes the business rule ("reject a dataset with more than 5%
null values") provable with plain unit tests, independent of any
infrastructure being up and running.

## What to notice

- `QualityThresholds` is a small object carrying `0.05`, not a hardcoded
  number buried in a method - because a number can only ever have one
  value, an object can be constructed differently per context.
- `DataQualityReport` is a **value object**, not an entity: no identity,
  just four numbers that make two instances equal if the numbers match.
  See [Glossary](Glossary#value-object).
- `is_acceptable` takes `thresholds` as a parameter instead of reading a
  global — that's what makes the boundary case (`null_ratio` exactly at
  the threshold) trivial to test without mocking anything.
- `DatasetRejectedError` carries the full `report`, not just a message
  string — a business failure that the application layer can inspect, not
  just a string to print.

## Why it matters for the rest of the project

Every later stage depends on this one staying pure. The moment a cloud SDK
import sneaks into `src/domain/`, the "swap providers without touching
business logic" premise of the whole project breaks. This is the layer to
protect most carefully as new adapters get added.

Back to [Home](Home) · Next: [02 · Tooling](02-Tooling)
