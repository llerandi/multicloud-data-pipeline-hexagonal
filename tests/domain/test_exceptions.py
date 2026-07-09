# tests/domain/test_exceptions.py

"""Unit tests for domain exceptions."""

import pytest

from src.domain.exceptions import DatasetRejectedError
from src.domain.models import DataQualityReport


def test_dataset_rejected_error_carries_the_report_and_reason():
    report = DataQualityReport(
        total_rows=100,
        null_count=20,
        duplicate_count=0,
        out_of_range_count=0,
    )

    error = DatasetRejectedError(report, "null ratio 0.20 exceeds max 0.05")

    assert error.report is report
    assert error.reason == "null ratio 0.20 exceeds max 0.05"
    assert str(error) == "null ratio 0.20 exceeds max 0.05"


def test_dataset_rejected_error_can_be_raised_and_caught():
    report = DataQualityReport(
        total_rows=10,
        null_count=1,
        duplicate_count=0,
        out_of_range_count=0,
    )

    with pytest.raises(DatasetRejectedError):
        raise DatasetRejectedError(report, "example failure")
