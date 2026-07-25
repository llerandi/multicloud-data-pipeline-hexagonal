"""Unit tests for CloudMonitoringMetricsPublisher.

FakeCloudMonitoringClient implements just the one method this adapter
calls, write_points, and records what it was given. Since the adapter
never imports google-cloud-monitoring, none of these tests need it
installed either.
"""

from src.application.ports import MetricsPublisher
from src.domain.models import DataQualityReport
from src.infrastructure.metrics import CloudMonitoringMetricsPublisher


class FakeCloudMonitoringClient:
    def __init__(self):
        self.calls = []

    def write_points(self, project_name, points):
        self.calls.append((project_name, points))


def test_cloud_monitoring_metrics_publisher_is_a_metrics_publisher():
    assert issubclass(CloudMonitoringMetricsPublisher, MetricsPublisher)


def test_publish_writes_one_point_per_report_field_with_the_dataset_label():
    client = FakeCloudMonitoringClient()
    publisher = CloudMonitoringMetricsPublisher(
        client, project_name="projects/my-project"
    )
    report = DataQualityReport(
        total_rows=100,
        null_count=5,
        duplicate_count=1,
        out_of_range_count=0,
    )

    publisher.publish("customers", report)

    assert len(client.calls) == 1
    project_name, points = client.calls[0]
    assert project_name == "projects/my-project"

    points_by_type = {point["metric_type"]: point for point in points}
    assert set(points_by_type) == {
        "custom.googleapis.com/data_quality/total_rows",
        "custom.googleapis.com/data_quality/null_count",
        "custom.googleapis.com/data_quality/null_ratio",
        "custom.googleapis.com/data_quality/duplicate_count",
        "custom.googleapis.com/data_quality/out_of_range_count",
    }
    assert points_by_type["custom.googleapis.com/data_quality/total_rows"]["value"] == 100
    assert points_by_type["custom.googleapis.com/data_quality/null_count"]["value"] == 5
    assert points_by_type["custom.googleapis.com/data_quality/null_ratio"]["value"] == 0.05

    for point in points:
        assert point["labels"] == {"dataset": "customers"}


def test_publish_labels_points_with_the_dataset_they_belong_to():
    client = FakeCloudMonitoringClient()
    publisher = CloudMonitoringMetricsPublisher(
        client, project_name="projects/my-project"
    )
    report = DataQualityReport(
        total_rows=10, null_count=0, duplicate_count=0, out_of_range_count=0
    )

    publisher.publish("orders", report)

    _, points = client.calls[0]
    assert all(point["labels"]["dataset"] == "orders" for point in points)
