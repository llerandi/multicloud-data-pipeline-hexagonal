"""Unit tests for the application ports.

A port is an abc.ABC with an abstractmethod, so there are only two
things worth testing at this stage: it cannot be instantiated on its
own, and a minimal concrete subclass that implements the abstract
method can be instantiated and called. The real behavior lives in the
infrastructure adapters, tested separately once they exist.
"""

import pytest

from src.application.ports import (
    DatasetRepository,
    FileStorage,
    MetricsPublisher,
    NotificationPort,
)
from src.domain.models import DataQualityReport


def test_file_storage_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        FileStorage()


def test_file_storage_concrete_subclass_works():
    class InMemoryFileStorage(FileStorage):
        def read(self, path: str) -> bytes:
            return b"content of " + path.encode()

    storage = InMemoryFileStorage()
    assert storage.read("dataset.csv") == b"content of dataset.csv"


def test_dataset_repository_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        DatasetRepository()


def test_dataset_repository_concrete_subclass_works():
    class InMemoryDatasetRepository(DatasetRepository):
        def __init__(self):
            self.saved = {}

        def save(self, dataset_name, rows):
            self.saved[dataset_name] = rows

    repository = InMemoryDatasetRepository()
    repository.save("customers", [{"id": 1}])
    assert repository.saved == {"customers": [{"id": 1}]}


def test_metrics_publisher_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        MetricsPublisher()


def test_metrics_publisher_concrete_subclass_works():
    class RecordingMetricsPublisher(MetricsPublisher):
        def __init__(self):
            self.published = []

        def publish(self, dataset_name, report):
            self.published.append((dataset_name, report))

    publisher = RecordingMetricsPublisher()
    report = DataQualityReport(
        total_rows=10,
        null_count=1,
        duplicate_count=0,
        out_of_range_count=0,
    )
    publisher.publish("customers", report)
    assert publisher.published == [("customers", report)]


def test_notification_port_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        NotificationPort()


def test_notification_port_concrete_subclass_works():
    class RecordingNotificationPort(NotificationPort):
        def __init__(self):
            self.failures = []

        def notify_failure(self, dataset_name, reason):
            self.failures.append((dataset_name, reason))

    notifier = RecordingNotificationPort()
    notifier.notify_failure("customers", "null ratio 0.20 exceeds max 0.05")
    assert notifier.failures == [("customers", "null ratio 0.20 exceeds max 0.05")]
