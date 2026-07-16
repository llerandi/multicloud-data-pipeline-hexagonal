# PR 12: S3FileStorage adapter

Branch: `feature/s3-file-storage-adapter`

Files added: `src/infrastructure/storage/s3_file_storage.py`,
`src/infrastructure/storage/__init__.py` (updated),
`tests/infrastructure/storage/test_s3_file_storage.py`,
`pyproject.toml` (updated).

`FileStorage` now has three adapters: local filesystem, GCS, and S3. This
is the comparison the project's original scope was built around, same
port, two real cloud providers with genuinely different client shapes,
so this file spends most of its space on that comparison rather than
repeating what PR 11 already covered about not importing the SDK and
about the not-found exception gap, both apply here identically.

## The same read(path) -> bytes contract, two different client shapes underneath

```python
# GcsFileStorage
def read(self, path: str) -> bytes:
    blob = self._bucket.blob(path)
    return blob.download_as_bytes()
```

```python
# S3FileStorage
def read(self, path: str) -> bytes:
    response = self._bucket.Object(path).get()
    return response["Body"].read()
```

GCS's client is object-oriented and verb-shaped: `bucket.blob(path)`
returns a reference, and that reference has a method that directly
answers the question being asked, `download_as_bytes()` returns exactly
that, bytes. boto3's resource API is shaped differently: `bucket.Object(path)`
also returns a reference, but calling `.get()` on it returns a plain
dict describing the response, HTTP-metadata-adjacent, with the actual
content nested behind a `"Body"` key as a stream object that itself
needs a separate `.read()` call to produce bytes. Neither shape is
wrong, they reflect two SDKs designed independently by two companies,
years apart, with different conventions.

`ValidateAndIngestDataset` calls `file_storage.read(path)` and gets
`bytes` back, full stop, in both cases. It does not know that one
adapter calls one method and the other calls two, on a completely
differently shaped object. That gap between "two real, meaningfully
different client libraries" and "one identical call from the use case's
point of view" is not a simplification the project is glossing over,
it is the actual thing hexagonal architecture is for. This is the same
observation the project scope opened with: switching cloud providers
should not require rewriting the business logic that decides whether a
dataset is good enough to use, and this pair of adapters is that claim
made concrete instead of theoretical.

## Everything else is the same reasoning as PR 11, on purpose

`S3FileStorage` does not import `boto3`, for the same reason
`GcsFileStorage` does not import `google-cloud-storage`: it is
constructed with a `bucket` resource already built and authenticated
elsewhere, and only calls the two methods it needs on it, which is what
lets its tests run with a `FakeBucket` and no real AWS credentials
anywhere near this project.

It also does not catch or translate the exception a missing key raises.
boto3 raises its own `botocore.exceptions.ClientError` for that, a third
distinct exception type, next to `FileNotFoundError` from
`LocalFileStorage` and GCS's `NotFound`. This is the same documented gap
as PR 11, now with three different answers instead of two, still written
down directly rather than quietly ignored, and still left as explicit
future work rather than solved by importing an SDK just to catch one
exception from it.

The test fakes follow the same principle as GCS's: `FakeBucket.Object(path)`
always succeeds, exactly like the real boto3 resource, and the failure
for a missing key is deferred to `.get()`, matching where it actually
happens in AWS, not moved to whichever method was more convenient to
fail in.

## `boto3` as its own `s3` extra

```toml
s3 = [
    "boto3>=1.34",
]
```

Same pattern as `sklearn`, `postgres`, and `gcs`: its own optional extra,
so `pip install -e ".[dev]"` stays light for anyone not touching this
adapter, and `pip install -e ".[dev,s3]"` opts in specifically when
needed.
