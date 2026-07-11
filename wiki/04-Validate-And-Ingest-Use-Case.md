# 04 · ValidateAndIngestDataset use case

Branch: `feature/validate-and-ingest-use-case` · Technical write-up:
[docs/04-validate-and-ingest-use-case.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/04-validate-and-ingest-use-case.md)

## The concept this stage teaches

This is where **dependency injection** stops being an abstract idea and
becomes the reason the project's central claim is actually true. The use
case's constructor takes all four ports as arguments - it never builds a
GCS client or a BigQuery client itself, anywhere. That single decision is
what makes it possible to test `ValidateAndIngestDataset` completely with
in-memory fakes today, and to later run the *exact same class* against
GCS+BigQuery in one environment and S3+Postgres in another, without
changing this file at all.

## What to notice

- "Compute the report from rows" logic lives in `src/domain/rules.py`, not
  as a method on the use case or on `DataQualityReport` - because
  deciding what counts as null or duplicate is a business decision, the
  same category as the 5% threshold itself, so it belongs in the domain.
- File parsing (CSV/JSON bytes → rows) lives on the use case, not the
  domain - it's a technical detail of *how this pipeline* ingests data,
  not a business rule, but it also doesn't belong in infrastructure since
  it needs no cloud SDK.
- `out_of_range_count` is hardcoded to `0`, explicitly, with a comment -
  not faked as a real check, because there's no schema yet to check
  against, and a fake check that always passes would look identical to a
  real one that found nothing wrong.
- The rejection test checks not just that the exception was raised, but
  that the repository and publisher were **not** called - a rejected
  dataset must not be half-persisted.

## Why it matters for the rest of the project

This use case is the thing every future adapter eventually plugs into. The
whole point of stages 05–08 (and everything pending in the
[Roadmap](Roadmap)) is proving that this class never needs to change as
the concrete infrastructure around it does.

Back to [Home](Home) · Previous: [03 · Application ports](03-Application-Ports) · Next: [05 · LocalFileStorage adapter](05-Local-Filesystem-Adapter)
