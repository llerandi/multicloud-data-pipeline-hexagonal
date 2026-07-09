"""LocalFileStorage: a FileStorage adapter backed by the local filesystem.

Meant for tests and local development, not production use. It exists so
the pipeline can be exercised end to end without needing a GCS or S3
account, and so the GCS and S3 adapters, once written, have something to
be compared against: the same FileStorage contract, three different
backends.
"""

from pathlib import Path
from typing import Union

from src.application.ports import FileStorage


class LocalFileStorage(FileStorage):
    """Reads files from a directory on the local disk.

    root_dir plays the same role a bucket name plays for GCS or S3: it
    is configured once, when the adapter is built, and every path
    passed to read() is resolved relative to it. That keeps the
    meaning of "path" in FileStorage.read consistent across adapters,
    a key relative to wherever this adapter's storage root is, never
    an absolute filesystem path, never a full gs:// or s3:// URL.
    """

    def __init__(self, root_dir: Union[str, Path]) -> None:
        self._root_dir = Path(root_dir)

    def read(self, path: str) -> bytes:
        """Return the raw bytes of root_dir/path.

        Lets FileNotFoundError propagate as-is if the file does not
        exist, rather than catching and re-raising a custom error.
        FileNotFoundError already carries the exact path that was
        missing, wrapping it would only hide that detail behind a new
        exception type, without making the failure clearer.
        """
        file_path = self._root_dir / path
        return file_path.read_bytes()
