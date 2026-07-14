# PR 11: GcsFileStorage adapter

Branch: `feature/gcs-file-storage-adapter`

Files added: `src/infrastructure/storage/gcs_file_storage.py`,
`src/infrastructure/storage/__init__.py` (updated),
`tests/infrastructure/storage/test_gcs_file_storage.py`,
`pyproject.toml` (updated).

This is the second `FileStorage` adapter, after `LocalFileStorage`, and
the first one backed by an actual cloud provider. Most of the reasoning
here already showed up for `PostgresDatasetRepository`, same shape, same
adapter. This file covers what changes for storage specifically.

## The adapter still does not import the SDK, for the same reason as Postgres

```python
"""
This module does not import google-cloud-storage at all. It only calls
.blob(path) and .download_as_bytes() on whatever bucket object it is
given, the same two calls any object shaped like a
google.cloud.storage.Bucket exposes.
"""
```

`GcsFileStorage` is constructed with a `bucket`, already built and
authenticated by whoever wires the pipeline together, exactly like
`PostgresDatasetRepository` is constructed with an already-open
connection. `read` calls `bucket.blob(path).download_as_bytes()` and
nothing else. Nothing in this file cares whether `bucket` is a real
`google.cloud.storage.Bucket` or `FakeBucket` from the test file, as long
as it responds to `.blob(path)` the same way. That is what lets this
adapter, and every test for it, run without `google-cloud-storage`
installed and without any GCP credentials anywhere near this project.

## Why `path` still means "a key inside the configured root", same as `LocalFileStorage`

`LocalFileStorage.read(path)` resolves `path` against `root_dir`.
`GcsFileStorage.read(path)` resolves `path` against `bucket`. Neither
takes a full `gs://bucket/path` URL or an absolute filesystem path,
`path` means the same thing regardless of which adapter is handling it:
a key relative to wherever this adapter's storage root already is. That
consistency, established back in PR 5, is what lets the application
layer call `file_storage.read(path)` without knowing or caring which of
the two adapters it is actually talking to, which is the entire point of
the port.

## The one thing this PR does not solve, and says so directly

```python
"""
Deliberately does not catch or translate whatever exception a missing
object raises. [...] This is a real, current inconsistency between
FileStorage adapters, not something quietly papered over.
"""
```

`LocalFileStorage.read` raises `FileNotFoundError` for a missing file,
because that is what `Path.read_bytes()` already raises, no translation
needed. A real GCS client raises its own `google.cloud.exceptions.NotFound`
for a missing object, a different exception type. Catching that and
re-raising `FileNotFoundError` for consistency would be the more polished
choice, but it requires importing something from `google-cloud-storage`
just to catch its exception, which is exactly the import this file is
built to avoid needing for anything else. Rather than quietly accept
that trade-off or silently ignore the inconsistency, it is written down
directly in the adapter's docstring: today, code calling `read()` across
different `FileStorage` adapters cannot rely on one exception type for
"this does not exist". Fixing that later, most likely by importing only
the specific exception classes needed to normalize this, is future work,
not something this PR pretends is already handled.

## The test fakes mirror the real client's actual behavior, not a simplified version of it

```python
class FakeBucket:
    def blob(self, path):
        if path in self._objects:
            return FakeBlob(content=self._objects[path], exists=True)
        return FakeBlob(exists=False)
```

In the real `google-cloud-storage` client, `bucket.blob(name)` always
succeeds, it just builds a reference object, it does not check whether
anything exists at that path. The check, and the failure for a missing
object, only happens later, when something is actually requested, on
`download_as_bytes()`. `FakeBucket.blob` mirrors that: it always returns
a `FakeBlob`, and the missing-object failure is deferred to that blob's
own `download_as_bytes()` call, the same place it would happen for real.
Writing the fake to fail at the wrong step, inside `blob()` instead of
inside `download_as_bytes()`, would still make the tests pass, but it
would be testing a version of GCS that does not actually exist.

## Why `google-cloud-storage` gets its own `gcs` extra, matching `sklearn` and `postgres`

```toml
gcs = [
    "google-cloud-storage>=2.10",
]
```

Same reasoning as the other two: this is a multi-cloud project on
purpose, and anyone working on a part of it that has nothing to do with
GCS should not need the Google Cloud SDK installed to do that work.
`pip install -e ".[dev]"` stays light, `pip install -e ".[dev,gcs]"` opts
in specifically for this adapter, the same pattern the S3 adapter will
follow with its own extra next.
