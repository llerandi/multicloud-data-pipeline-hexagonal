"""FileStorage port.

Reads the raw contents of a dataset file. Adapters implement this
against a specific location (GCS, S3, local filesystem). The
application layer only needs the bytes back, it does not know or care
where they came from.
"""

from abc import ABC, abstractmethod


class FileStorage(ABC):
    """Abstract contract for reading a raw dataset file."""

    @abstractmethod
    def read(self, path: str) -> bytes:
        """Return the raw contents of the file at path.

        path is a plain string on purpose. Each adapter decides what
        it means: a local filesystem path, a GCS object name, an S3
        key. The application layer passes it through without
        inspecting it.
        """
        raise NotImplementedError
