"""Unit tests for LocalFileStorage.

tmp_path is a built-in pytest fixture: it gives each test its own fresh
temporary directory, cleaned up automatically, so these tests touch the
real filesystem without ever needing to clean up after themselves or
risk colliding with another test.
"""

import pytest

from src.application.ports import FileStorage
from src.infrastructure.storage import LocalFileStorage


def test_local_file_storage_is_a_file_storage():
    # Guards against LocalFileStorage drifting away from the port it is
    # supposed to implement, the same abc enforcement described in the
    # ports PR would catch a missing method, this just makes the
    # relationship explicit.
    assert issubclass(LocalFileStorage, FileStorage)


def test_read_returns_the_exact_bytes_written_to_a_file(tmp_path):
    (tmp_path / "dataset.csv").write_bytes(b"id,email\n1,a@b.com\n")
    storage = LocalFileStorage(root_dir=tmp_path)

    content = storage.read("dataset.csv")

    assert content == b"id,email\n1,a@b.com\n"


def test_read_raises_file_not_found_for_a_missing_file(tmp_path):
    storage = LocalFileStorage(root_dir=tmp_path)

    with pytest.raises(FileNotFoundError):
        storage.read("missing.csv")


def test_read_is_scoped_to_root_dir_not_the_process_working_directory(tmp_path):
    subdir = tmp_path / "datasets"
    subdir.mkdir()
    (subdir / "dataset.json").write_bytes(b"[]")

    storage = LocalFileStorage(root_dir=subdir)

    assert storage.read("dataset.json") == b"[]"
