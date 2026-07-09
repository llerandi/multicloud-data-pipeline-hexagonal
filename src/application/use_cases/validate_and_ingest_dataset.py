"""ValidateAndIngestDataset use case.

Coordinates the whole pipeline for one dataset: read the raw file,
parse it into rows, compute its quality report, apply the business
rule, and either persist it and publish its metrics, or notify that it
was rejected.

This class knows the steps of the pipeline. It does not know which
cloud provider each port talks to, that is decided entirely by which
adapters get passed into its constructor.
"""

import csv
import io
import json
from typing import Any, Mapping, Optional, Sequence

from src.application.ports import (
    DatasetRepository,
    FileStorage,
    MetricsPublisher,
    NotificationPort,
)
from src.domain.exceptions import DatasetRejectedError
from src.domain.models import DataQualityReport, QualityThresholds
from src.domain.rules import compute_quality_report


class ValidateAndIngestDataset:
    """Reads, validates, and persists one dataset, one file at a time."""

    def __init__(
        self,
        file_storage: FileStorage,
        dataset_repository: DatasetRepository,
        metrics_publisher: MetricsPublisher,
        notification_port: NotificationPort,
        thresholds: Optional[QualityThresholds] = None,
    ) -> None:
        self._file_storage = file_storage
        self._dataset_repository = dataset_repository
        self._metrics_publisher = metrics_publisher
        self._notification_port = notification_port
        # Falls back to the default thresholds (5% max null ratio) if the
        # caller does not provide its own, rather than making every caller
        # repeat the default.
        self._thresholds = thresholds or QualityThresholds()

    def execute(self, dataset_name: str, path: str) -> DataQualityReport:
        """Run the pipeline for the file at path and return its report.

        Raises DatasetRejectedError, after sending a failure
        notification, if the dataset does not meet the quality rule.
        The dataset is only saved and its metrics only published if it
        passes.
        """
        raw = self._file_storage.read(path)
        rows = self._parse_rows(path, raw)
        report = compute_quality_report(rows)

        if not report.is_acceptable(self._thresholds):
            reason = (
                f"null ratio {report.null_ratio:.2%} exceeds the maximum "
                f"of {self._thresholds.max_null_ratio:.2%}"
            )
            self._notification_port.notify_failure(dataset_name, reason)
            raise DatasetRejectedError(report, reason)

        self._dataset_repository.save(dataset_name, rows)
        self._metrics_publisher.publish(dataset_name, report)
        return report

    @staticmethod
    def _parse_rows(path: str, raw: bytes) -> Sequence[Mapping[str, Any]]:
        """Turn raw file bytes into a list of row dictionaries.

        The format is decided by the file extension in path. Only CSV
        and JSON are supported, matching the project scope, and both
        parsers come from the standard library so this use case does
        not need pandas or any other dependency just to read a file.
        """
        if path.endswith(".json"):
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, list):
                raise ValueError("JSON dataset must be a list of records")
            return data
        if path.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
            return list(reader)
        raise ValueError(f"unsupported file extension for path: {path}")
