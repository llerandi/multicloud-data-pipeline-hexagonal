"""Integration test: ValidateAndIngestDataset wired to a real FileStorage.

Every other test so far replaces every port with an in-memory fake.
This one is different on purpose: LocalFileStorage is the real adapter,
reading an actual file from an actual temporary directory on disk. The
other three ports are still fakes, because DatasetRepository,
MetricsPublisher and NotificationPort do not have a real adapter yet.

This is the first test in the project where "the use case" and "a real
piece of infrastructure" are proven to work together, instead of just
each being correct on its own.
"""

import pytest

from src.application.ports import DatasetRepository, MetricsPublisher, NotificationPort
from src.application.use_cases import ValidateAndIngestDataset
from src.domain.exceptions import DatasetRejectedError
from src.infrastructure.storage import LocalFileStorage


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


def test_use_case_reads_a_real_file_from_disk_and_ingests_it(tmp_path):
    (tmp_path / "customers.csv").write_bytes(
        b"id,email\n1,a@b.com\n2,c@d.com\n3,e@f.com\n"
    )

    use_case = ValidateAndIngestDataset(
        file_storage=LocalFileStorage(root_dir=tmp_path),
        dataset_repository=(repository := FakeDatasetRepository()),
        metrics_publisher=(publisher := FakeMetricsPublisher()),
        notification_port=(notifier := FakeNotificationPort()),
    )

    report = use_case.execute("customers", "customers.csv")

    assert report.total_rows == 3
    assert report.null_count == 0
    assert repository.saved["customers"] == [
        {"id": "1", "email": "a@b.com"},
        {"id": "2", "email": "c@d.com"},
        {"id": "3", "email": "e@f.com"},
    ]
    assert publisher.published == [("customers", report)]
    assert notifier.failures == []


def test_use_case_rejects_a_real_file_with_too_many_nulls(tmp_path):
    (tmp_path / "customers.csv").write_bytes(
        b"id,email\n1,\n2,\n3,e@f.com\n"
    )

    use_case = ValidateAndIngestDataset(
        file_storage=LocalFileStorage(root_dir=tmp_path),
        dataset_repository=(repository := FakeDatasetRepository()),
        metrics_publisher=FakeMetricsPublisher(),
        notification_port=(notifier := FakeNotificationPort()),
    )

    with pytest.raises(DatasetRejectedError):
        use_case.execute("customers", "customers.csv")

    assert "customers" not in repository.saved
    assert len(notifier.failures) == 1
