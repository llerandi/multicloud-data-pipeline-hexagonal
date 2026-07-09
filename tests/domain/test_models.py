# tests/domain/test_models.py

"""Unit tests for the domain models.

These tests only import from src.domain, no infrastructure, no
mocking of external services. That is the point of keeping business
rules in the domain layer: they can be verified with plain, fast
tests.
"""

from src.domain.models import DataQualityReport, QualityThresholds


def test_null_ratio_computes_fraction_of_null_rows():
    report = DataQualityReport(
        total_rows=100,
        null_count=10,
        duplicate_count=0,
        out_of_range_count=0,
    )

    assert report.null_ratio == 0.1


def test_null_ratio_is_zero_for_empty_dataset():
    report = DataQualityReport(
        total_rows=0,
        null_count=0,
        duplicate_count=0,
        out_of_range_count=0,
    )

    assert report.null_ratio == 0.0


def test_dataset_is_acceptable_when_null_ratio_is_below_threshold():
    report = DataQualityReport(
        total_rows=100,
        null_count=4,
        duplicate_count=0,
        out_of_range_count=0,
    )
    thresholds = QualityThresholds(max_null_ratio=0.05)

    assert report.is_acceptable(thresholds) is True


def test_dataset_is_acceptable_at_exactly_the_threshold():
    report = DataQualityReport(
        total_rows=100,
        null_count=5,
        duplicate_count=0,
        out_of_range_count=0,
    )
    thresholds = QualityThresholds(max_null_ratio=0.05)

    assert report.is_acceptable(thresholds) is True


def test_dataset_is_rejected_when_null_ratio_exceeds_threshold():
    report = DataQualityReport(
        total_rows=100,
        null_count=6,
        duplicate_count=0,
        out_of_range_count=0,
    )
    thresholds = QualityThresholds(max_null_ratio=0.05)

    assert report.is_acceptable(thresholds) is False
