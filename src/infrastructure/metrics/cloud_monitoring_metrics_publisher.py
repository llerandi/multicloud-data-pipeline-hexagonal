"""CloudMonitoringMetricsPublisher: a MetricsPublisher adapter backed by
Cloud Monitoring.

Every adapter written before this one could duck-type a single, simple
method the real SDK's own client already exposes: psycopg's cursor,
GCS's blob, boto3's bucket object, BigQuery's insert_rows_json. Cloud
Monitoring does not offer an equivalent: writing a custom metric there
means building a TimeSeries, a MonitoredResource, and one or more Points
with a typed value and a time interval, all as protobuf message objects
from the google-cloud-monitoring SDK itself. There is no single method
on the real client this adapter could call with plain arguments the way
the others do.

So this module defines its own plain shape instead of the SDK's: a
"point" is just a dict with a metric name, a numeric value, and a dict
of labels. Translating a list of these into real Cloud Monitoring
TimeSeries objects is left to whatever client wrapper actually gets
constructed and injected here, this adapter's job stops at deciding what
to publish and in what shape, not at speaking Cloud Monitoring's wire
format directly.
"""

from typing import Any

from src.application.ports import MetricsPublisher
from src.domain.models import DataQualityReport


class CloudMonitoringMetricsPublisher(MetricsPublisher):
    """Publishes a DataQualityReport as a set of Cloud Monitoring points.

    client is expected to already be authenticated against a specific
    GCP project, and to expose one method, write_points(project_name,
    points), same role a connection plays for PostgresDatasetRepository
    or a bucket plays for GcsFileStorage: a ready-to-use collaborator,
    not the configuration needed to build one.

    project_name is the fully qualified "projects/<project-id>" string
    Cloud Monitoring's real API expects, kept as a plain string here
    since this adapter never touches the SDK that would otherwise
    validate its shape.
    """

    def __init__(self, client: Any, project_name: str) -> None:
        self._client = client
        self._project_name = project_name

    def publish(self, dataset_name: str, report: DataQualityReport) -> None:
        """Publish every numeric field on report as its own point.

        One point per field rather than one point carrying every field
        as separate values, because Cloud Monitoring itself models a
        metric as one named, timestamped number, a "null_ratio" metric
        and a "duplicate_count" metric are two different things to
        query or alert on later, not two fields of one blob. dataset_name
        is attached to every point as a label, so metrics for different
        datasets stay distinguishable once they reach Cloud Monitoring.
        """
        labels = {"dataset": dataset_name}
        points = [
            self._point("total_rows", report.total_rows, labels),
            self._point("null_count", report.null_count, labels),
            self._point("null_ratio", report.null_ratio, labels),
            self._point("duplicate_count", report.duplicate_count, labels),
            self._point("out_of_range_count", report.out_of_range_count, labels),
        ]
        self._client.write_points(self._project_name, points)

    @staticmethod
    def _point(metric_name: str, value: Any, labels: dict) -> dict:
        return {
            "metric_type": f"custom.googleapis.com/data_quality/{metric_name}",
            "value": value,
            "labels": labels,
        }
