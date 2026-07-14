"""GcsFileStorage: a FileStorage adapter backed by a Google Cloud Storage
bucket.

Same reasoning as PostgresDatasetRepository: this module does not import
google-cloud-storage at all. It only calls .blob(path) and
.download_as_bytes() on whatever bucket object it is given, the same two
calls any object shaped like a google.cloud.storage.Bucket exposes. The
real dependency only shows up wherever a real bucket gets constructed
and authenticated, not here, which is what keeps this adapter testable
with a plain fake instead of a real GCS bucket and real credentials.
"""

from typing import Any

from src.application.ports import FileStorage


class GcsFileStorage(FileStorage):
    """Reads objects from a GCS bucket using a caller-supplied bucket.

    bucket is expected to already be a configured
    google.cloud.storage.Bucket, or anything shaped like one, built and
    authenticated by whoever constructs this class. Just like
    LocalFileStorage's root_dir plays the role a bucket name plays for
    a cloud adapter, bucket here plays that same role directly: path
    passed to read() is always a key inside it, never a full gs://
    URL, keeping FileStorage.read's meaning identical across every
    adapter that implements it.
    """

    def __init__(self, bucket: Any) -> None:
        self._bucket = bucket

    def read(self, path: str) -> bytes:
        """Return the raw bytes of the object named path in this bucket.

        Deliberately does not catch or translate whatever exception a
        missing object raises. The real google-cloud-storage client
        raises its own google.cloud.exceptions.NotFound for that case,
        not the FileNotFoundError LocalFileStorage raises, and this
        adapter does not import that exception type just to catch it,
        the same reason it does not import the rest of the SDK. This
        is a real, current inconsistency between FileStorage adapters,
        not something quietly papered over: today, code calling
        FileStorage.read across different adapters cannot rely on a
        single exception type for "the file does not exist", closing
        that gap, most likely by importing just the exception classes
        needed to normalize this, is left as explicit future work.
        """
        blob = self._bucket.blob(path)
        return blob.download_as_bytes()
