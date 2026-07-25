# 11 · GcsFileStorage adapter

Branch: `feature/gcs-file-storage-adapter` · Technical write-up:
[docs/11-gcs-file-storage-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/11-gcs-file-storage-adapter.md)

## The concept this stage teaches

The second `FileStorage` adapter, and the first backed by a real cloud
provider. Same reasoning as [10](10-·-PostgresDatasetRepository-adapter):
constructed with an already-authenticated `bucket`, calls only
`.blob(path).download_as_bytes()` on it, never imports
`google-cloud-storage`. The concept worth sitting with here isn't the
mechanism - it's that `path` keeps meaning exactly the same thing
(a key relative to wherever this adapter's storage root already is) as it
did for `LocalFileStorage` in [05](05-·-LocalFileStorage-adapter). That
consistency is the entire point of the port: the application layer never
needs to know which adapter it's talking to.

## What to notice

- The adapter deliberately does **not** catch or translate the exception
  a missing object raises - a real GCS client raises
  `google.cloud.exceptions.NotFound`, not `FileNotFoundError`. Rather than
  quietly living with that inconsistency or importing the SDK just to
  catch one exception from it, the gap is written down directly in the
  code. Honesty about an unsolved edge case, not a false sense of
  polish.
- The test fake mirrors *where* a real failure happens, not just *that*
  it happens: `bucket.blob(path)` always succeeds and returns a
  reference (matching the real client), the missing-object failure is
  deferred to `download_as_bytes()`, the same place it would occur for
  real. A fake that failed at the wrong step would still pass tests while
  testing a GCS that doesn't actually exist.
- `google-cloud-storage` gets its own `gcs` extra, same pattern started
  in [09](09-·-SklearnModelInference-adapter).

## Why it matters for the rest of the project

[12](12-·-S3FileStorage-adapter) is the payoff: the same `read(path) ->
bytes` contract, implemented against a completely differently shaped
SDK. This page is the "before" half of that comparison.

Back to [Home](Home) · Previous: [10 · PostgresDatasetRepository adapter](10-·-PostgresDatasetRepository-adapter) · Next: [12 · S3FileStorage adapter](12-·-S3FileStorage-adapter)
