"""Unit tests for S3FileStorage.

The fakes below mirror boto3's actual resource shape, not a simplified
stand-in for it: bucket.Object(path) always succeeds and only returns a
reference, .get() is what actually fails for a missing key, and a
successful .get() returns a dict with a "Body" that itself needs a
.read() call, not the bytes directly. Since the adapter never imports
boto3, none of this needs it installed either.
"""

import pytest

from src.application.ports import FileStorage
from src.infrastructure.storage import S3FileStorage


class FakeStreamingBody:
    def __init__(self, content):
        self._content = content

    def read(self):
        return self._content


class FakeS3Object:
    def __init__(self, content=None, exists=True):
        self._content = content
        self._exists = exists

    def get(self):
        if not self._exists:
            raise LookupError("key does not exist")
        return {"Body": FakeStreamingBody(self._content)}


class FakeBucket:
    def __init__(self, objects):
        self._objects = objects

    def Object(self, path):
        if path in self._objects:
            return FakeS3Object(content=self._objects[path], exists=True)
        return FakeS3Object(exists=False)


def test_s3_file_storage_is_a_file_storage():
    assert issubclass(S3FileStorage, FileStorage)


def test_read_returns_the_bytes_stored_under_that_key():
    bucket = FakeBucket({"dataset.csv": b"id,email\n1,a@b.com\n"})
    storage = S3FileStorage(bucket=bucket)

    content = storage.read("dataset.csv")

    assert content == b"id,email\n1,a@b.com\n"


def test_read_lets_the_bucket_s_missing_key_error_propagate_unchanged():
    bucket = FakeBucket({})
    storage = S3FileStorage(bucket=bucket)

    # LookupError here stands in for the botocore.exceptions.ClientError
    # a real S3 bucket raises for a missing key, this adapter does not
    # catch or translate it, see the docstring on S3FileStorage.read.
    with pytest.raises(LookupError):
        storage.read("missing.csv")
