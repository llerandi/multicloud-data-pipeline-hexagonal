"""Storage adapters implementing the FileStorage port (GCS, S3, local filesystem)."""

from src.infrastructure.storage.local_file_storage import LocalFileStorage

__all__ = ["LocalFileStorage"]
