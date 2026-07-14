"""Unit tests for GcsFileStorage.

FakeBucket and FakeBlob below implement just the two calls this adapter
actually makes, .blob(path) and .download_as_bytes(), matching how the
real google-cloud-storage client behaves: blob() always succeeds and
just returns a reference, download_as_bytes() is what actually fails
for an object that does not exist. Since the adapter never imports
google-cloud-storage, none of this needs it installed either.
"""

import pytest

from src.application.ports import FileStorage
from src.infrastructure.storage import GcsFileStorage


class FakeBlob:
    def __init__(self, content=None, exists=True):
        self._content = content
        self._exists = exists

    def download_as_bytes(self):
        if not self._exists:
            raise LookupError("blob does not exist")
        return self._content


class FakeBucket:
    def __init__(self, objects):
        self._objects = objects

    def blob(self, path):
        if path in self._objects:
            return FakeBlob(content=self._objects[path], exists=True)
        return FakeBlob(exists=False)


def test_gcs_file_storage_is_a_file_storage():
    assert issubclass(GcsFileStorage, FileStorage)


def test_read_returns_the_bytes_stored_under_that_path():
    bucket = FakeBucket({"dataset.csv": b"id,email\n1,a@b.com\n"})
    storage = GcsFileStorage(bucket=bucket)

    content = storage.read("dataset.csv")

    assert content == b"id,email\n1,a@b.com\n"


def test_read_lets_the_bucket_s_not_found_error_propagate_unchanged():
    bucket = FakeBucket({})
    storage = GcsFileStorage(bucket=bucket)

    # LookupError here stands in for whatever exception a real GCS
    # client raises for a missing object, this adapter does not catch
    # or translate it, see the docstring on GcsFileStorage.read for why.
    with pytest.raises(LookupError):
        storage.read("missing.csv")
