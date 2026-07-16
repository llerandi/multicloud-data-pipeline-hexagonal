"""S3FileStorage: a FileStorage adapter backed by an S3 bucket.

Same reasoning as GcsFileStorage and PostgresDatasetRepository: this
module does not import boto3 at all. It only calls .Object(path) and
.get() on whatever bucket resource it is given, and reads the "Body"
key off the result, the same shape any object built like a boto3 S3
Bucket resource exposes. The real dependency only shows up wherever a
real bucket resource gets constructed and authenticated, not here.
"""

from typing import Any

from src.application.ports import FileStorage


class S3FileStorage(FileStorage):
    """Reads objects from an S3 bucket using a caller-supplied bucket resource.

    bucket is expected to already be a configured boto3 S3 Bucket
    resource (for example, boto3.resource("s3").Bucket(name)), or
    anything shaped like one, built and authenticated by whoever
    constructs this class. Same role root_dir plays for
    LocalFileStorage and bucket plays for GcsFileStorage: path passed
    to read() is a key inside it, never a full s3:// URL.
    """

    def __init__(self, bucket: Any) -> None:
        self._bucket = bucket

    def read(self, path: str) -> bytes:
        """Return the raw bytes of the object named path in this bucket.

        boto3's resource API shapes this differently from GCS:
        bucket.Object(path) returns a reference (like GCS's
        bucket.blob(path)), but calling .get() on it returns a plain
        dict, not the bytes directly, with the actual content behind a
        "Body" key as a stream that still needs its own .read() call.
        Both client shapes end up looking completely different from
        each other, and both are hidden behind the exact same
        FileStorage.read(path) -> bytes contract, which is the point of
        having a port at all: this difference is the adapter's problem
        to deal with, not the use case's.

        Like GcsFileStorage, this does not catch or translate the
        exception a missing key raises. boto3 raises its own
        botocore.exceptions.ClientError for that case, a third
        exception type, different from both FileNotFoundError and
        GCS's NotFound. Importing botocore just to catch that one
        exception would reintroduce the SDK dependency this file is
        built to avoid, so, same as GcsFileStorage, this is a known,
        documented gap rather than a silently accepted one.
        """
        response = self._bucket.Object(path).get()
        return response["Body"].read()
