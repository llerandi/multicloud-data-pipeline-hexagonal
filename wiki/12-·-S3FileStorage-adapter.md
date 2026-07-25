# 12 · S3FileStorage adapter

Branch: `feature/s3-file-storage-adapter` · Technical write-up:
[docs/12-s3-file-storage-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/12-s3-file-storage-adapter.md)

## The concept this stage teaches

`FileStorage` now has three adapters, and this is where the project's
founding claim stops being theoretical: "switching cloud provider without
rewriting the business rules" made concrete, not just asserted. GCS's
client is verb-shaped - `bucket.blob(path).download_as_bytes()` returns
bytes directly. boto3's is shaped completely differently -
`bucket.Object(path).get()` returns a dict, with the actual content
nested behind a `"Body"` key that itself needs a separate `.read()`.
Two SDKs, designed independently, years apart, with different
conventions - and `ValidateAndIngestDataset` ([04](04-·-ValidateAndIngestDataset-use-case))
calls `file_storage.read(path)` and gets `bytes` back either way, never
knowing the difference.

## What to notice

- Compare the two `read` implementations side by side (see the
  write-up) - that gap between "two meaningfully different libraries"
  and "one identical call from the use case's point of view" isn't a
  simplification the project glosses over. It's the actual thing
  hexagonal architecture buys you.
- Same duck-typing discipline as [11](11-·-GcsFileStorage-adapter): no
  `boto3` import, constructed with an already-built `bucket` resource.
- Now a *third* distinct not-found exception type joins the list
  (`FileNotFoundError`, GCS's `NotFound`, and boto3's
  `botocore.exceptions.ClientError`) - same documented gap as
  [11](11-·-GcsFileStorage-adapter), still tracked as future work in
  [Roadmap](Roadmap-and-status), not solved by guessing.
- `boto3` gets its own `s3` extra, same pattern as `sklearn`, `postgres`,
  `gcs`.

## Why it matters for the rest of the project

This page is the clearest illustration in the whole project of what a
port actually buys you. Worth reading immediately after
[11](11-·-GcsFileStorage-adapter) rather than on its own.

Back to [Home](Home) · Previous: [11 · GcsFileStorage adapter](11-·-GcsFileStorage-adapter) · Next: [13 · BigqueryDatasetRepository adapter](13-·-BigqueryDatasetRepository-adapter)
