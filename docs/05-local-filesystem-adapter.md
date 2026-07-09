# PR 5: LocalFileStorage adapter

Branch: `feature/local-filesystem-adapter`

Files added: `src/infrastructure/storage/local_file_storage.py`,
`src/infrastructure/storage/__init__.py` (updated),
`tests/infrastructure/storage/test_local_file_storage.py`,
`tests/integration/test_local_pipeline.py`.

## The first adapter, and why it is the local filesystem and not GCS

This is the first class in the project that implements a port instead of
just defining one. It implements `FileStorage`, backed by the local disk,
which is not meant for production, it exists so the pipeline can be
exercised for real (reading actual bytes from an actual file) without
needing a GCS bucket, an S3 bucket, or any cloud credentials at all. It is
also what the GCS and S3 adapters, whenever they get written, will be
compared against: the same three methods on the same port, three
different places the bytes actually come from.

## Why `root_dir` is a constructor argument instead of `read` taking a full path

```python
class LocalFileStorage(FileStorage):
    def __init__(self, root_dir):
        self._root_dir = Path(root_dir)

    def read(self, path: str) -> bytes:
        return (self._root_dir / path).read_bytes()
```

A GCS adapter needs a bucket name to know where to look, an S3 adapter
needs a bucket name too, neither of them gets the bucket name from the
`path` argument passed to `read`, they get it when the adapter itself is
constructed, and `read` only receives the key inside that bucket.
`LocalFileStorage` is built to match that shape on purpose: `root_dir`
plays the role a bucket name plays for the cloud adapters, configured
once, and `path` is always relative to it, whatever it means, a plain
filename or a nested `datasets/customers.csv`. Keeping `read`'s parameter
meaning consistent across every `FileStorage` adapter is what lets the
application layer call `file_storage.read(path)` without needing to know
or care which adapter it is actually talking to.

## Why a missing file raises `FileNotFoundError` unchanged

```python
def read(self, path: str) -> bytes:
    file_path = self._root_dir / path
    return file_path.read_bytes()
```

`Path.read_bytes()` already raises `FileNotFoundError` with the exact
path that was missing if the file does not exist. This adapter does not
catch it and re-raise something else. Wrapping it in a custom exception
would not add information, it would only hide the original, already
clear, error behind a new type that callers would then have to learn
about. Letting a well-known standard library exception propagate is
sometimes the simplest correct choice, not a shortcut.

## What the unit tests check, using `tmp_path`

```python
def test_read_returns_the_exact_bytes_written_to_a_file(tmp_path):
    (tmp_path / "dataset.csv").write_bytes(b"...")
    storage = LocalFileStorage(root_dir=tmp_path)
    ...
```

`tmp_path` is a built-in pytest fixture, pytest creates a fresh, empty
temporary directory for each test that asks for it (by naming it as a
parameter) and deletes it afterward. That is what lets these tests touch
the real filesystem, no mocking of `open()` or `Path`, while staying
fast, isolated from each other, and leaving nothing behind. Besides the
happy path, there is a test for a missing file (checks the exception,
not just that something raises) and a test that writes the file inside a
subdirectory used as `root_dir`, to confirm paths really are resolved
relative to `root_dir` and not to wherever the test process happens to be
running from.

## The integration test: the first one that is not all fakes

Every test written so far for the use case replaces all four ports with
in-memory fakes. `tests/integration/test_local_pipeline.py` is
deliberately different: `LocalFileStorage` is real, reading an actual
file from an actual temporary directory, while `DatasetRepository`,
`MetricsPublisher` and `NotificationPort` are still fakes, because they
do not have real adapters yet.

This is worth having as its own test, separate from the unit tests for
`LocalFileStorage` and separate from the unit tests for
`ValidateAndIngestDataset`, because each of those two already proves its
own class is correct in isolation, neither proves they actually work
together. A wiring mistake, for example if `LocalFileStorage.read`
returned a `str` instead of `bytes`, would not necessarily be caught by
either unit test suite on its own, but would break this one immediately,
since the use case calls `raw.decode("utf-8")` on whatever `read`
returns.

`tests/integration/` is a new top-level folder, alongside `tests/domain`,
`tests/application` and `tests/infrastructure`, specifically for tests
that exercise more than one layer at once. As more real adapters are
built, this is where their combinations with the use case belong.
