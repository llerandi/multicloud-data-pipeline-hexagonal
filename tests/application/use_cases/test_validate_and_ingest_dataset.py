"""Unit tests for the ValidateAndIngestDataset use case.

Every port is replaced by a small in-memory fake, not a mocking
library. Each fake is a real subclass of the port's ABC, which means
these tests only compile at all if the fakes correctly implement the
same contract a real GCS or BigQuery adapter would have to.
"""

import pytest

from src.application.ports import (
    DatasetRepository,
    FileStorage,
    MetricsPublisher,
    NotificationPort,
)
from src.application.use_cases import ValidateAndIngestDataset
from src.domain.exceptions import DatasetRejectedError
from src.domain.models import QualityThresholds


class FakeFileStorage(FileStorage):
    def __init__(self, files):
        self._files = files

    def read(self, path):
        return self._files[path]


class FakeDatasetRepository(DatasetRepository):
    def __init__(self):
        self.saved = {}

    def save(self, dataset_name, rows):
        self.saved[dataset_name] = rows


class FakeMetricsPublisher(MetricsPublisher):
    def __init__(self):
        self.published = []

    def publish(self, dataset_name, report):
        self.published.append((dataset_name, report))


class FakeNotificationPort(NotificationPort):
    def __init__(self):
        self.failures = []

    def notify_failure(self, dataset_name, reason):
        self.failures.append((dataset_name, reason))


def _build_use_case(files):
    file_storage = FakeFileStorage(files)
    dataset_repository = FakeDatasetRepository()
    metrics_publisher = FakeMetricsPublisher()
    notification_port = FakeNotificationPort()

    use_case = ValidateAndIngestDataset(
        file_storage=file_storage,
        dataset_repository=dataset_repository,
        metrics_publisher=metrics_publisher,
        notification_port=notification_port,
    )
    return use_case, dataset_repository, metrics_publisher, notification_port


def test_execute_saves_and_publishes_metrics_for_a_valid_csv_dataset():
    csv_content = b"id,email\n1,a@b.com\n2,c@d.com\n"
    use_case, repository, publisher, notifier = _build_use_case(
        {"customers.csv": csv_content}
    )

    report = use_case.execute("customers", "customers.csv")

    assert report.total_rows == 2
    assert report.null_count == 0
    assert repository.saved["customers"] == [
        {"id": "1", "email": "a@b.com"},
        {"id": "2", "email": "c@d.com"},
    ]
    assert publisher.published == [("customers", report)]
    assert notifier.failures == []


def test_execute_parses_a_valid_json_dataset():
    json_content = b'[{"id": "1", "email": "a@b.com"}, {"id": "2", "email": "c@d.com"}]'
    use_case, repository, publisher, notifier = _build_use_case(
        {"customers.json": json_content}
    )

    report = use_case.execute("customers", "customers.json")

    assert report.total_rows == 2
    assert repository.saved["customers"] == [
        {"id": "1", "email": "a@b.com"},
        {"id": "2", "email": "c@d.com"},
    ]
    assert notifier.failures == []


def test_execute_rejects_a_dataset_with_too_many_nulls_and_notifies():
    # 2 out of 3 rows are missing an email, a null ratio of 0.67, well
    # above the default 5% threshold.
    csv_content = b"id,email\n1,\n2,\n3,c@d.com\n"
    use_case, repository, publisher, notifier = _build_use_case(
        {"customers.csv": csv_content}
    )

    with pytest.raises(DatasetRejectedError):
        use_case.execute("customers", "customers.csv")

    assert "customers" not in repository.saved
    assert publisher.published == []
    assert len(notifier.failures) == 1
    assert notifier.failures[0][0] == "customers"


def test_execute_accepts_custom_thresholds():
    # Same 67% null ratio as above, but this time with a threshold
    # loose enough to accept it, proving the use case actually uses
    # the thresholds it was given instead of a hardcoded value.
    csv_content = b"id,email\n1,\n2,\n3,c@d.com\n"
    file_storage = FakeFileStorage({"customers.csv": csv_content})
    dataset_repository = FakeDatasetRepository()
    metrics_publisher = FakeMetricsPublisher()
    notification_port = FakeNotificationPort()

    use_case = ValidateAndIngestDataset(
        file_storage=file_storage,
        dataset_repository=dataset_repository,
        metrics_publisher=metrics_publisher,
        notification_port=notification_port,
        thresholds=QualityThresholds(max_null_ratio=0.9),
    )

    report = use_case.execute("customers", "customers.csv")

    assert dataset_repository.saved["customers"] is not None
    assert report.null_count == 2


def test_execute_raises_for_unsupported_file_extension():
    use_case, _, _, _ = _build_use_case({"customers.txt": b"whatever"})

    with pytest.raises(ValueError):
        use_case.execute("customers", "customers.txt")
