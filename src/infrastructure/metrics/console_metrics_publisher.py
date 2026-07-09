"""ConsoleMetricsPublisher: a MetricsPublisher adapter that prints to stdout.

Meant for local development, not production. It exists so the pipeline
has somewhere to send its metrics before a real Cloud Monitoring adapter
is written, and so that future adapter has something to be compared
against: the same MetricsPublisher contract, one backend that prints,
one that calls a cloud API.
"""

from src.application.ports import MetricsPublisher
from src.domain.models import DataQualityReport


class ConsoleMetricsPublisher(MetricsPublisher):
    """Prints a DataQualityReport to stdout instead of sending it anywhere.

    The fields are printed as key=value pairs on one line, on purpose:
    that format is both readable by a person watching the terminal and
    easy to grep or parse if this ever gets piped somewhere, without
    needing a real structured-logging setup for what is, for now, a
    development-only adapter.
    """

    def publish(self, dataset_name: str, report: DataQualityReport) -> None:
        print(
            f"[metrics] dataset={dataset_name} "
            f"total_rows={report.total_rows} "
            f"null_count={report.null_count} "
            f"null_ratio={report.null_ratio:.2%} "
            f"duplicate_count={report.duplicate_count} "
            f"out_of_range_count={report.out_of_range_count}"
        )
