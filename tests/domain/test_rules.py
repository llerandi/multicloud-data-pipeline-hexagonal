"""Unit tests for src.domain.rules.compute_quality_report."""

from src.domain.rules import compute_quality_report


def test_total_rows_matches_number_of_rows():
    rows = [{"id": "1"}, {"id": "2"}, {"id": "3"}]

    report = compute_quality_report(rows)

    assert report.total_rows == 3


def test_none_values_count_as_null():
    rows = [{"id": "1", "email": None}, {"id": "2", "email": "a@b.com"}]

    report = compute_quality_report(rows)

    assert report.null_count == 1


def test_empty_string_values_count_as_null():
    rows = [{"id": "1", "email": ""}, {"id": "2", "email": "a@b.com"}]

    report = compute_quality_report(rows)

    assert report.null_count == 1


def test_zero_and_false_do_not_count_as_null():
    rows = [{"id": "1", "score": 0, "active": False}]

    report = compute_quality_report(rows)

    assert report.null_count == 0


def test_first_occurrence_of_a_row_is_not_a_duplicate():
    rows = [{"id": "1"}, {"id": "2"}]

    report = compute_quality_report(rows)

    assert report.duplicate_count == 0


def test_repeated_row_counts_as_one_duplicate():
    rows = [{"id": "1"}, {"id": "1"}, {"id": "2"}]

    report = compute_quality_report(rows)

    assert report.duplicate_count == 1


def test_out_of_range_count_is_always_zero_for_now():
    rows = [{"id": "1"}]

    report = compute_quality_report(rows)

    assert report.out_of_range_count == 0
