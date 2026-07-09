"""Unit tests for ConsoleMetricsPublisher.

capsys is a built-in pytest fixture that captures whatever a test
writes to stdout and stderr, so the assertions here check the actual
printed text instead of trusting that print() was called correctly.
"""

from src.application.ports import MetricsPublisher
from src.domain.models import DataQualityReport
from src.infrastructure.metrics import ConsoleMetricsPublisher


def test_console_metrics_publisher_is_a_metrics_publisher():
    assert issubclass(ConsoleMetricsPublisher, MetricsPublisher)


def test_publish_prints_the_dataset_name_and_report_fields(capsys):
    publisher = ConsoleMetricsPublisher()
    report = DataQualityReport(
        total_rows=100,
        null_count=5,
        duplicate_count=1,
        out_of_range_count=0,
    )

    publisher.publish("customers", report)

    captured = capsys.readouterr()
    assert "dataset=customers" in captured.out
    assert "total_rows=100" in captured.out
    assert "null_count=5" in captured.out
    assert "null_ratio=5.00%" in captured.out
    assert "duplicate_count=1" in captured.out
    assert "out_of_range_count=0" in captured.out


def test_publish_writes_exactly_one_line_per_call(capsys):
    publisher = ConsoleMetricsPublisher()
    report = DataQualityReport(
        total_rows=10,
        null_count=0,
        duplicate_count=0,
        out_of_range_count=0,
    )

    publisher.publish("customers", report)
    publisher.publish("orders", report)

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2
    assert "dataset=customers" in lines[0]
    assert "dataset=orders" in lines[1]
