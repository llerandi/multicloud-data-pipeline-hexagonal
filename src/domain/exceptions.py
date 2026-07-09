# src/domain/exceptions.py

"""Domain exceptions for the data quality pipeline.

These represent business failures, not technical ones. A
DatasetRejectedError means the data itself did not meet the rules, as
opposed to, say, a network error talking to GCS. Keeping this
distinction in the domain layer lets the application layer decide how
to react (notify, log, retry) without inspecting infrastructure
exceptions.
"""

from src.domain.models import DataQualityReport


class DatasetRejectedError(Exception):
    """Raised when a dataset fails the data quality rules.

    Carries the report that caused the rejection so the caller (a use
    case, a notification adapter) can explain why the dataset was
    refused instead of just knowing that it was.
    """

    def __init__(self, report: DataQualityReport, reason: str) -> None:
        self.report = report
        self.reason = reason
        super().__init__(reason)
